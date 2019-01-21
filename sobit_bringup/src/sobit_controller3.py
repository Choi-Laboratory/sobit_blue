#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import rospy
import readchar
import math
from sensor_msgs.msg import *
from geometry_msgs.msg import *

ser=serial.Serial(
  		port = '/dev/vsrc',
   	baudrate = 115200,
 	 	parity = serial.PARITY_NONE, 
 	 	bytesize = serial.EIGHTBITS,
 	 	stopbits = serial.STOPBITS_ONE,
   	timeout = None,
   	xonxoff = 0,
   	rtscts = 0,
#   	interCharTimeout = None
)

#グローバル変数
VEL = 0
ANG = 0
L_motion_cm = 0
R_motion_cm = 0
L_motion_vel = 0
R_motion_vel = 0
D = 16		#2D:tread
time = 0.1	#送信モーションの単位時間ｓ（Default:0.1）
seq = 0

enc_jointstate = JointState()
enc_jointstate.name =["L_wheel","R_wheel","L_shoulder_roll","L_shoulder_pitch","L_elbow_yaw","L_shoulder_pitch","R_shoulder_roll","R_shoulder_pitch","R_elbow_yaw","R_elbow_pitch","neck_pitch","neck_roll","neck_yaw","L_hand_twist","L_hand_thumb","L_hand_index","L_hand_mid","L_hand_ring","L_hand_pinky","R_hand_twist"]

state_jointstate = JointState()
state_jointstate.name =["L_wheel","R_wheel","L_shoulder_roll","L_shoulder_pitch","L_elbow_yaw","L_shoulder_pitch","R_shoulder_roll","R_shoulder_pitch","R_elbow_yaw","R_elbow_pitch","neck_pitch","neck_roll","neck_yaw","L_hand_twist","L_hand_thumb","L_hand_index","L_hand_mid","L_hand_ring","L_hand_pinky","R_hand_twist"]

####初期設定#########################################################################################################
def first_set():
			print "[First_set]"

			print "<pose_init>"	
			ser.write("@00c8:T8000:T8000:T8000:T0000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000::::::T8000:T8000:T6800:T9800:T6800:T9800:T8000:T8000:T9800:T6800:T9800:T6800\n")
			print ser.readline(),
			rospy.sleep(1)

			print "<R>"
			ser.write("R\n")
			print ser.readline(),
			rospy.sleep(1)

			print "<get_enc>"
			ser.write(":Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx::::::T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx\n");
			print ser.readline(),
			rospy.sleep(1)

			print "<gain_on>"
			ser.write(":P0100:P0100:P0040:P0080:P0045:P0040:P0040:P0080:P0045:P0040:P0080:P0200:P0016::::::P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001\n")
			print ser.readline(),
			rospy.sleep(1)


####cul_motion##############################################################################################
def cul_motion(vel,ang,position):
			global L_motion_vel
			global R_motion_vel
			global L_motion_cm
			global R_motion_cm
			global D
			global time
			motion = [0]*21
			motion_deg = [0]*21
			motion_in = 0

			print "\n[CUL_MOTION]"
			
			#print "vel:",+vel 	#vel:速度[m/s]
			#print "ang:",+ang 	#ang:角速度[rad/s]
			#print "time:",+time 	#time:単位時間[s]
			#print "position:"
			#print position
			#print position[3]

			###CUL_WHEEL############################################################################
			vel = vel * 100 #translate 'm' to 'cm' 
			
			#左右車輪の速度の計算
			L_motion_vel = (vel - 2 * ang * D)  
			R_motion_vel = (vel + 2 * ang * D)

 			#左右車輪
			L_motion_cm += L_motion_vel * time
			R_motion_cm += R_motion_vel * time
			print "L_motion_cm:",+L_motion_cm
			print "R_motion_cm:",+R_motion_cm

			#初期化
			L_motion_vel = 0
			R_motion_vel = 0
			motion_in = 0
			vel = 0

			###CUL_POSITION################################################################################
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
			motion[0] = '%04x' %(time * 40)
			
			motion[1] = '%04x' %(32768 + L_motion_cm * 60)		#<L_wheel>
			motion[2] = '%04x' %(32768 - R_motion_cm * 60)		#<R_wheel>
		
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

			print "motion:"
			print motion

			return motion


####エンコーダ取得##############################################################################################################
def get_enc():
			global seq
			position_enc2 = [0]*30

			print "\n[ENCODER]"

			print "<get_enc>"
			ser.write(":Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx::::::T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx\n");
			str = ser.readline(),
			#print str[0]
			position_enc = str[0].split(";")		#各関節値に「;」で分割
			#print position_enc

			for i in range(1,31):
				position_enc[i] = position_enc[i][1:]				#最初の文字(C)削除
				if len(position_enc[i]) != 0:
					position_enc[i] = int(position_enc[i],16)		#16進数→10進数
				else:
					pass

			#print position_enc

			#print position_enc[0]

			#cm変換
			position_enc[1] = (position_enc[1] - 32768)/44 
			position_enc[2] = (position_enc[2] - 32768)/44		
			position_enc[3] = (position_enc[3] - 32768)/97		#<L_shoulder_roll>
			#position_enc[4] = (position_enc[4] - 32768)/86		#<L_shoulder_pitch>
			position_enc[5] = (position_enc[5] - 32768)/58		#<L_elbow_yaw>
			position_enc[6] = (position_enc[6] - 32768)/105		#<L_elbow_pitch>
			position_enc[7] = (position_enc[7] - 32768)/97		#<R_shoulder_roll>
			position_enc[8] = (position_enc[8] - 32768)/86		#<R_shoulder_pitch>
			position_enc[9] = (position_enc[9] - 32768)/58		#<R_elbow_yaw>
			position_enc[10] = (position_enc[10] - 32768)/105	#<R_elbow_pitch>
			position_enc[11] = (position_enc[11] - 32768)/110	#<neck_pitch>
			position_enc[12] = (position_enc[12] - 32768)/112	#<neck_roll>	
			position_enc[13] = (position_enc[13] - 32768)/246	#<neck yaw>
			position_enc[19] = (position_enc[19] - 32768)/91	#<L_hand_twist>
			position_enc[20] = (position_enc[20] - 32768)/91	#<L_hand_thumb>
			position_enc[21] = (position_enc[21] - 26624)/68	#<L_hand_index>
			position_enc[22] = (position_enc[22] - 38912)/68	#<L_hand_middle>
			position_enc[23] = (position_enc[23] - 26624)/68	#<L_hand_ring>
			position_enc[24] = (position_enc[24] - 38912)/68	#<L_hand_index>	
			position_enc[25] = (position_enc[25] - 32768)/91	#<R_hand_twist>

			#print position_enc

			#rad変換
			position_enc[1] = (position_enc[1] * 3.14)/180 
			position_enc[2] = (position_enc[2] * 3.14)/180
			position_enc[3] = (position_enc[3] * 3.14)/180		#<L_shoulder_roll>
			#position_enc[4] = (position_enc[4] * 3.14)/180		#<L_shoulder_pitch>
			position_enc[5] = (position_enc[5] * 3.14)/180		#<L_elbow_yaw>
			position_enc[6] = (position_enc[6] * 3.14)/180		#<L_elbow_pitch>
			position_enc[7] = (position_enc[7] * 3.14)/180		#<R_shoulder_roll>
			position_enc[8] = (position_enc[8] * 3.14)/180		#<R_shoulder_pitch>
			position_enc[9] = (position_enc[9] * 3.14)/180		#<R_elbow_yaw>
			position_enc[10] = (position_enc[10] * 3.14)/180	#<R_elbow_pitch>
			position_enc[11] = (position_enc[11] * 3.14)/180	#<neck_pitch>
			position_enc[12] = (position_enc[12] * 3.14)/180	#<neck_roll>	
			position_enc[13] = (position_enc[13] * 3.14)/180	#<neck yaw>
			position_enc[19] = (position_enc[19] * 3.14)/180	#<L_hand_twist>
			position_enc[20] = (position_enc[20] * 3.14)/180	#<L_hand_thumb>
			position_enc[21] = (position_enc[21] * 3.14)/180	#<L_hand_index>
			position_enc[22] = (position_enc[22] * 3.14)/180	#<L_hand_middle>
			position_enc[23] = (position_enc[23] * 3.14)/180	#<L_hand_ring>
			position_enc[24] = (position_enc[24] * 3.14)/180	#<L_hand_index>	
			position_enc[25] = (position_enc[25] * 3.14)/180	#<R_hand_twist>

			#print position_enc

			#time
			now = rospy.get_rostime()
			
			#enc_jointstateの更新
			enc_jointstate.header.seq = seq
			enc_jointstate.header.stamp.secs = now.secs
			enc_jointstate.header.stamp.nsecs = now.nsecs
			enc_jointstate.position = (position_enc[1],position_enc[2],position_enc[3],position_enc[4],position_enc[5],position_enc[6],position_enc[7],position_enc[8],position_enc[9],position_enc[10],position_enc[11],position_enc[12],position_enc[13],position_enc[19],position_enc[20],position_enc[21],position_enc[22],position_enc[23],position_enc[24],position_enc[25])
			#enc_jointstate.velocity = (left_joint_vel,right_joint_vel)

			#確認表示
			print enc_jointstate

			seq = seq + 1

			return enc_jointstate


####callback1########################################################################################################
def callback1(jointstate):
			global state_jointstate
			global VEL
			global ANG
			pub = rospy.Publisher('sobit_enc', JointState , queue_size=10)		

			print "\n\n[CALL_BACK1]"
			now = rospy.get_rostime()
			test = now.nsecs - jointstate.header.stamp.nsecs 
			print "test:",test 
			if now.secs - jointstate.header.stamp.secs > 1:
				return

			#print jointstate

			state_jointstate.position = jointstate.position

			#print state_jointstate

			#エンコーダ
			enc_jointstate_2 = JointState()
			enc_jointstate_2 = get_enc()		
			print	"enc_jointtate:", enc_jointstate_2
			pub.publish(enc_jointstate_2)

			rospy.sleep(0.05)	


			print state_jointstate.position

			#速度から距離とモーションタイムを計算
			motion = cul_motion(VEL,ANG,state_jointstate.position)
			

			#モーションの送信		
			print "[MOTION_SEND]"
			#print motion
			ser.write("@"+motion[0]+":T"+motion[1]+":T"+motion[2]+":T"+motion[3]+":T0000:T"+motion[5]+":T"+motion[6]+":T"+motion[7]+":T"+motion[8]+":T"+motion[9]+":T"+motion[10]+":T"+motion[11]+":T"+motion[12]+":T"+motion[13]+"::::::T"+motion[14]+":T"+motion[15]+":T"+motion[16]+":T"+motion[17]+":T"+motion[18]+":T"+motion[19]+":T"+motion[20]+":T8000:T9800:T6800:T9800:T6800\n")
			print ser.readline(),

			rospy.sleep(0.05)

			


####callback2########################################################################################################
def callback2(cmd_vel):		
			global VEL
			global ANG
			print "\n\n[CALL_BACK2]"

			VEL = cmd_vel.linear.x
			ANG = cmd_vel.angular.z


####メイン関数#################################################################################################################
if __name__ == '__main__':
			global VEL
			global ANG
			global state_jointstate

			#初期設定
			first_set()
			rospy.init_node('sobit_controller')	
			
			print "\nIf you want to end this program, push 'ctrlC' and next 'q' key!"
			

			#関節position指示の取得
			sub = rospy.Subscriber('sobit/joint_states', JointState, callback1)

			#cmd_velの読み込み
			sub = rospy.Subscriber('sobit/cmd_vel', Twist, callback2)

			rospy.spin()	

			#キー入力(q)で終了
			#kb = readchar.readchar()
			#if kb == "q":
			print("[exit program]")
			print "<pose_init>"	
			ser.write("@012c:T8000:T8000:T8000:T0000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000::::::T8000:T8000:T6800:T9800:T6800:T9800:T8000:T8000:T9800:T6800:T9800:T6800\n")
			print ser.readline(),
			rospy.sleep(3)

			print "<gain_off>"
			ser.write("P0000\n")
			print ser.readline(),

			



