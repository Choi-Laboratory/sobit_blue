#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import rospy
import readchar
import math
from sensor_msgs.msg import *
from geometry_msgs.msg import *
from sobit_bringup.msg import *


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

first_JOINT_flag = True
first_CMD_flag = True
LAST_joint = str()
LAST_cmd = str()
seq = 0
FLAG = True
enc_jointstate = JointState()
enc_jointstate.name =["L_wheel","R_wheel","L_shoulder_roll","L_shoulder_pitch","L_elbow_yaw","L_shoulder_pitch","R_shoulder_roll","R_shoulder_pitch","R_elbow_yaw","R_elbow_pitch","neck_pitch","neck_roll","neck_yaw","L_hand_twist","L_hand_thumb","L_hand_index","L_hand_mid","L_hand_ring","L_hand_pinky","R_hand_twist"]


####初期設定------------------------------------------------------------------------------------------------
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

			seq = seq + 1



####[CALLBACK]-------------------------------------------------------------------------------------
def callback(msg):
			global first_JOINT_flag, first_CMD_flag, LAST_joint, LAST_cmd, FLAG

			print "\n[callback]"
			#print "msg:",msg
			#print "LAST_joint:",LAST_joint

			get_enc()
			rospy.sleep(0.01)

			if msg.name == 'JOINT':
				if first_JOINT_flag == True:
					LAST_joint = msg.serial
					first_JOINT_flag = False

				if msg.serial == LAST_joint:
					print "joint:skip"
					LAST_joint = msg.serial									
					return
				LAST_joint = msg.serial
				
			if msg.name == 'CMD':
				if first_CMD_flag == True:
					LAST_cmd = msg.serial
					first_CMD_flag = False

				if msg.serial == LAST_cmd:
					print "cmd:skip"
					LAST_cmd = msg.serial									
					return
				LAST_cmd = msg.serial

			send_motion = msg.serial

			#モーションの送信
			print "[motion_send]",send_motion
			ser.write(send_motion)
			print ser.readline(),
			rospy.sleep(0.01)
		
			

####[メイン関数]#################################################################################################################
if __name__ == '__main__':
			first_set()	#初期設定
			rospy.init_node('sobit_controller')
			print "\nIf you want to end this program, push 'ctrlC' key!"
			
			#トピックの取得
			sub = rospy.Subscriber('serial_msg', Serial_motion, callback)			
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
			


