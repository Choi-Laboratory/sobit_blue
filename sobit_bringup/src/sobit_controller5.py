#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import rospy
import readchar
import math
from sensor_msgs.msg import *
from geometry_msgs.msg import *

#シリアル通信設定
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

#---palamater--------------------------------
D = 16		#2D=tread(車輪の幅)
TIME = 0.1	#送信モーションの単位時間ｓ（Default:0.1）


#---グローバル変数-----------------------------
motion = [0]*21
L_motion_cm = 0
R_motion_cm = 0
seq = 0
CMD_TIME = rospy.Time()
CMD_first_flag = True
WHEEL_FLAG = False
UPPER_FLAG = False


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


####[エンコーダ取得]--------------------------------------------------------------------------------------------------
def get_enc():
			global seq
			global enc_jointstate
			print "\n[GET ENCODER]"

			#エンコーダの取得
			ser.write(":Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx::::::T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx\n");
			str = ser.readline(),
			#print str[0]

			#エンコーダの値を各関節値ごとに「;」で分割
			position_enc = str[0].split(";")		
			print position_enc

			#文字列の処理
			for i in range(1,31):
				position_enc[i] = position_enc[i][1:]	#最初の文字(C)削除
				if len(position_enc[i]) != 0:
					position_enc[i] = int(position_enc[i],16)
				else:
					pass

			#確認用
			#print position_enc
			#print position_enc[0]

			#パルスの計算
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

			#確認表示
			print	"enc_jointstate:",enc_jointstate.position

			#エンコーダ情報の送信
			pub = rospy.Publisher('sobit_enc', JointState , queue_size=1)		#publisherの定義
			pub.publish(enc_jointstate)
			rospy.sleep(0.01)	

			seq = seq + 1


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


####[車輪の計算]-----------------------------------------------------------------------------------------
def cul_wheel(vel,ang,delta_T):
			global L_motion_cm, R_motion_cm, D
			
			print "[CUL_WHEEL]"
			print "vel:",vel 			#vel:速度[m/s]
			print "ang:",ang 			#ang:角速度[rad/s]
			print "time:",delta_T 	#time:単位時間[s]

			#左右車輪の速度の計算
			vel = vel * 100 #translate 'm' to 'cm' 
			L_motion_vel = (vel - 2 * ang * D)
			R_motion_vel = (vel + 2 * ang * D)

 			#左右車輪
			L_motion_cm += L_motion_vel * delta_T
			R_motion_cm += R_motion_vel * delta_T
			print "L_motion_cm:",L_motion_cm
			print "R_motion_cm:",R_motion_cm

			#シリアルパルス化
			motion[0] = '%04x' %(delta_T * 40)
			motion[1] = '%04x' %(32768 + L_motion_cm * 52)			#<L_wheel>
			motion[2] = '%04x' %(32768 - R_motion_cm * 52.1)		#<R_wheel>

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

			#衝突回避フラグの確認
			if	WHEEL_FLAG == True:
				while WHEEL_FLAG == False:
					print "wait now"
			
			#モーションの送信	
			UPPER_FLAG = True
			print "[JOINT_MOTION_SEND]"
			ser.write("@"+motion[0]+":::T"+motion[3]+":T0000:T"+motion[5]+":T"+motion[6]+":T"+motion[7]+":T"+motion[8]+":T"+motion[9]+":T"+motion[10]+":T"+motion[11]+":T"+motion[12]+":T"+motion[13]+"::::::T"+motion[14]+":T"+motion[15]+":T"+motion[16]+":T"+motion[17]+":T"+motion[18]+":T"+motion[19]+":T"+motion[20]+":::::\n")
			print ser.readline(),
			rospy.sleep(0.01)	
			
			#エンコーダ取得
			get_enc()
			UPPER_FLAG == False
			rospy.sleep(0.02)	

			return

####[CMD_VEL CALLBACK]-------------------------------------------------------------------------------------
def callback2(cmd_vel):	
			global CMD_first_flag, CMD_LAST_TIME, WHEEL_FLAG
			print "\n\n[cmd_vel:CALLBACK]"

			vel = cmd_vel.linear.x
			ang = cmd_vel.angular.z

			if CMD_first_flag == True:	#初回のみ
				CMD_LAST_TIME = rospy.Time.now()	
				CMD_first_flag = False

			#ΔTの計算
			now = rospy.Time.now()
			delta_T = now - CMD_LAST_TIME
			delta_T = delta_T.to_sec()
			CMD_LAST_TIME = now	#次回処理用に格納	

			#車輪モーションの計算
			motion = cul_wheel(vel,ang,delta_T)
			print "wheel_motion:",motion
			
			if	UPPER_FLAG == True:
				while UPPER_FLAG == False:
					print "wait now"
			
			#車輪モーションの送信
			WHEEL_FLAG = True
			print "[WHEEL_MOTION_SEND]"
			#ser.write("@"+motion[0]+":T"+motion[1]+":T"+motion[2]+"::::::::::::::::::::::::::::\n")
			#print ser.readline(),
			rospy.sleep(0.02)			
			WHEEL_FLAG = False
			

			return


def talker():
			print "talker"
	
def listner():
			print "B"
			sub = rospy.Subscriber('sobit/joint_states', JointState, callback1)	#joint_state
			sub = rospy.Subscriber('sobit/cmd_vel', Twist, callback2)				#cmd_vel
			return

####[メイン関数]#################################################################################################################
if __name__ == '__main__':
			first_set()	#初期設定
			rospy.init_node('sobit_controller')
			print "\nIf you want to end this program, push 'ctrlC' and next 'q'key!"
			
			#トピックの取得
			while True:
				talker()
				listner()
				print "A"
				rospy.spin()

				#キー入力(ctrlC)で終了
				print("[exit program]")
				rospy.sleep(1)
				print "<pose_init>"	
				ser.write("@012c:T8000:T8000:T8000:T0000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000::::::T8000:T8000:T6800:T9800:T6800:T9800:T8000:T8000:T9800:T6800:T9800:T6800\n")
				print ser.readline(),
				rospy.sleep(5)
				print "<gain_off>"
				ser.write("P0000\n")
				print ser.readline(),
				break
				



