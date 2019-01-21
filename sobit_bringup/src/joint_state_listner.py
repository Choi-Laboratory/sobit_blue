#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import math
from sensor_msgs.msg import *
from geometry_msgs.msg import *
from sobit_bringup.msg import *

#---グローバル変数-----------------------------
motion = [0]*21
TIME = 0.1
serial_joint = Serial_motion()

state_jointstate = JointState()
state_jointstate.name =["L_wheel","R_wheel","L_shoulder_roll","L_shoulder_pitch","L_elbow_yaw","L_shoulder_pitch","R_shoulder_roll","R_shoulder_pitch","R_elbow_yaw","R_elbow_pitch","neck_pitch","neck_roll","neck_yaw","L_hand_twist","L_hand_thumb","L_hand_index","L_hand_mid","L_hand_ring","L_hand_pinky","R_hand_twist"]



####[上半身モーションの計算]-------------------------------------------------------------------
def cul_upper_motion(position):
			motion_deg = [0]*21
			
			print "\n[CUL_UPEER_MOTION]"
			
			#print "position:",position

			#rad2deg			
			motion_deg[2] = position[2] * 57.29		#<L_shoulder_roll>
			motion_deg[3] = position[3] * 57.29		#<L_shoulder_pitch>
			motion_deg[4] = position[4] * 57.29		#<L_elbow_yaw>
			motion_deg[5] = position[5] * 57.29		#<L_elbow_pitch>
			motion_deg[6] = position[6] * 57.29		#<R_shoulder_roll>
			motion_deg[7] = position[7] * 57.29		#<R_shoulder_pitch>
			motion_deg[8] = position[8] * 57.29		#<R_elbow_yaw>	
			motion_deg[9] = position[9] * 57.29		#<R_elbow_pitch>
			motion_deg[10] = position[10] * 57.29	#<neck_pitch>
			motion_deg[11] = position[11] * 57.29	#<neck_roll>	
			motion_deg[12] = position[12] * 57.29	#<neck yaw>
			motion_deg[13] = position[13] * 57.29	#<L_hand_twist>
			motion_deg[14] = position[14] * 57.29	#<L_hand_thumb>	
			motion_deg[15] = position[15] * 57.29	#<L_hand_index>	
			motion_deg[16] = position[16] * 57.29	#<L_hand_middle>	
			motion_deg[17] = position[17] * 57.29	#<L_hand_ring>		
			motion_deg[18] = position[18] * 57.29	#<L_hand_pinky>

			motion_deg[19] = position[19] * 57.29	#<R_hand_twist>

			#10→16進
			motion[0] = '%04x' %(TIME * 40)
		
			motion[3] = '%04x' %(32768 + motion_deg[2] * 97)		#<L_shoulder_roll>
			motion[4] = '%04x' %(32768 + motion_deg[3] * 86)		#<L_shoulder_pitch>
			motion[5] = '%04x' %(32768 + motion_deg[4] * 58)		#<L_elbow_yaw>
			motion[6] = '%04x' %(32768 - motion_deg[5] * 105)		#<L_elbow_pitch>	
			motion[7] = '%04x' %(32768 - motion_deg[6] * 97)		#<R_shoulder_roll>
			motion[8] = '%04x' %(32768 - motion_deg[7] * 86)		#<R_shoulder_pitch>
			motion[9] = '%04x' %(32768 - motion_deg[8] * 58)		#<R_elbow_yaw>	
			motion[10] = '%04x' %(32768 + motion_deg[9] * 105)		#<R_elbow_pitch>
			motion[11] = '%04x' %(32768 + motion_deg[10] * 110)	#<neck_pitch>
			motion[12] = '%04x' %(32768 + motion_deg[11] * 112)	#<neck_roll>	
			motion[13] = '%04x' %(32768 + motion_deg[12] * 246)	#<neck yaw>	
			motion[14] = '%04x' %(32768 - motion_deg[13] * 91)		#<L_hand_twist>
			motion[15] = '%04x' %(32768 - motion_deg[14] * 91)		#<L_hand_thumb>		
			motion[16] = '%04x' %(26624 - motion_deg[15] * 68)		#<L_hand_index>		
			motion[17] = '%04x' %(38912 + motion_deg[16] * 68)		#<L_hand_middle>		
			motion[18] = '%04x' %(26624 - motion_deg[17] * 68)		#<L_hand_ring>		
			motion[19] = '%04x' %(38912 + motion_deg[18] * 68)		#<L_hand_pinky>	
			motion[20] = '%04x' %(32768 + motion_deg[19] * 91)		#<R_hand_twist>

			print "motion:",motion

			return motion


####[JOINT_STATE CALLBACK]-------------------------------------------------------------------------------------
def callback1(jointstate):
			global state_jointstate, UPPER_FLAG
			print "\n\n[JOINT:CALLBACK]"

			#print jointstate
			
			#1秒以上古いjointstateの切り捨て
			now = rospy.get_rostime()
			test = now.nsecs - jointstate.header.stamp.nsecs 
			print "test:",test 
			if now.secs - jointstate.header.stamp.secs > 1:
				print "skip"
				return

			#ポジション情報の格納
			state_jointstate.position = jointstate.position
			print state_jointstate.position

			#上半身モーションの計算
			motion = cul_upper_motion(state_jointstate.position)
			print "upper_motion:",motion

			
			serial_joint.name = "JOINT"
			serial_joint.serial = "@"+motion[0]+":::T"+motion[3]+"::T"+motion[5]+":T"+motion[6]+":T"+motion[7]+":T"+motion[8]+":T"+motion[9]+":T"+motion[10]+":T"+motion[11]+":T"+motion[12]+":T"+motion[13]+"::::::T"+motion[14]+":T"+motion[15]+":T"+motion[16]+":T"+motion[17]+":T"+motion[18]+":T"+motion[19]+":T"+motion[20]+":::::\n"
			
			print serial_joint
			
			#シリアル信号の送信
			pub = rospy.Publisher('serial_msg', Serial_motion , queue_size=5)		#publisherの定義
			pub.publish(serial_joint)
			
			

			



####[メイン関数]#################################################################################################################
if __name__ == '__main__':
			rospy.init_node('joint_listner')

			sub = rospy.Subscriber('sobit/joint_states', JointState, callback1)	#joint_state
			rospy.spin()




