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
L_motion_cm = 0
R_motion_cm = 0
L_motion_vel = 0
R_motion_vel = 0
D = 16		#2D:tread
enc_jointstate = JointState()
enc_jointstate.name = ("left_wheel_joint","right_wheel_joint")
seq = 0

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


####cul_wheel##############################################################################################
def cul_wheel(vel,ang):
			global L_motion_vel
			global R_motion_vel
			global L_motion_cm
			global R_motion_cm
			global D
			motion = [0]*3
			motion_in = 0
			time = 0.1

			#単位時間あたりの移動距離
			print "vel:",+vel 	#vel:速度[m/s]
			print "ang:",+ang 	#ang:角速度[rad/s]
			#print "time:",+time 	#time:単位時間[s]

			vel = vel * 100 #translate 'm' to 'cm' 
			#motion_ang = (ang * 180 /math.pi) * 0.35 #0.35は回転1度あたりの定数（要調整）
			#print "motion_in:",+motion_in
			
			#左右車輪の速度の計算
			L_motion_vel = (vel - 2 * ang * D)  
			R_motion_vel = (vel + 2 * ang * D)
 			#左右車輪
			L_motion_cm += L_motion_vel * time
			R_motion_cm += R_motion_vel * time

			#モーションの計算
			#if ang == 0: #前後直進
			#		L_motion_cm += motion_in
			#		R_motion_cm += motion_in

			#elif ang < 0: #右回転
			#		L_motion_cm += motion_in
			#		L_motion_cm -= motion_ang
			#		R_motion_cm += motion_in
			#		R_motion_cm += motion_ang

			#elif ang > 0: #左回転
			#		L_motion_cm += motion_in
			#		L_motion_cm -= motion_ang
			#		R_motion_cm += motion_in
			#		R_motion_cm += motion_ang
			
			#初期化
			L_motion_vel = 0
			R_motion_vel = 0
			motion_in = 0
			vel = 0

			print "L_motion_cm:",+L_motion_cm
			print "R_motion_cm:",+R_motion_cm

			#10→16進
			motion[0] = '%04x' %(time * 40)
			motion[1] = '%x' %(32768 + L_motion_cm * 44)
			motion[2] = '%x' %(32768 - R_motion_cm * 44)

			return motion


####cul_jointstate.velocity##############################################################################################
#def cul_vel(position_enc):





####エンコーダ取得##############################################################################################################
def get_enc():
			global seq
			
			print "<get_enc>"
			ser.write(":Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx::::::T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx\n");
			str = ser.readline(),
			#print str[0]
			position_enc = str[0].split(";")
			
			for i in range(1,31):
				position_enc[i] = position_enc[i][1:]	#最初の文字(C)削除

			position_enc[30] = position_enc[30][:4]	#4桁化修正

			#10進数化修正
			left_joint10 = int(position_enc[1],16)
			right_joint10 = int(position_enc[2],16)
			#print "left :",+ left_joint10
			#print "right:",+ right_joint10

			#cm変換
			left_joint_cm = (left_joint10 - 32768)/44 
			right_joint_cm = (right_joint10 - 32768)/44
			print "left :",+ left_joint_cm
			print "right:",+ right_joint_cm
			
			#rad変換
			left_joint_deg = left_joint_cm *3.14 /180
			right_joint_deg = right_joint_cm *3.14 /180
			#print "left :",+ left_joint_deg
			#print "right:",+ right_joint_deg

			#time
			now = rospy.get_rostime()
			
			#cul_vel()

			#enc_jointstateの更新
			enc_jointstate.header.seq = seq
			enc_jointstate.header.stamp.secs = now.secs
			enc_jointstate.header.stamp.nsecs = now.nsecs
			enc_jointstate.position = (left_joint_deg,right_joint_deg)
			#enc_jointstate.velocity = (left_joint_vel,right_joint_vel)

			#確認表示
			#print enc_jointstate

			seq = seq + 1

			return enc_jointstate


####callback########################################################################################################
def callback2(joint_state):



####callback########################################################################################################
def callback(cmd_vel):
			pub = rospy.Publisher('sobit_enc_joint', JointState , queue_size=10)	
	
			#エンコーダ取得とjointstate出力
			enc_jointstate_2 = JointState()
			enc_jointstate_2 = get_enc()
			print ""			
			#print	enc_jointstate_2

			pub.publish(enc_jointstate_2)
			rospy.sleep(0.05)	

			sub = rospy.Subscriber('jointstate_publisher', JointState, callback2)

			#0の時は何もしない
			if cmd_vel.linear.x == 0 and cmd_vel.angular.z == 0:
				return
	
			#速度から距離とモーションタイムを計算
			motion = cul_wheel(cmd_vel.linear.x,cmd_vel.angular.z)

			#モーションの送信		
			print "[MOTION_SEND]"
			#print motion
			ser.write("@"+motion[0]+":T"+motion[1]+":T"+motion[2]+":T8000:T0000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000::::::T8000:T8000:T6800:T9800:T6800:T9800:T8000:T8000:T9800:T6800:T9800:T6800\n")
			print ser.readline(),
			rospy.sleep(0.05)


			return




####メイン関数#################################################################################################################
if __name__ == '__main__':
			#初期設定
			first_set()
			rospy.init_node('sobit_controller')	
			print "\nIf you want to end this program, push 'ctrlC' and next 'q' key!"
			
			#処理ループ
			while True:
				#cmd_velの読み込み
				sub = rospy.Subscriber('cmd_vel_mux/input/teleop', Twist, callback)

				rospy.spin()
	
				#キー入力(q)で終了
				kb = readchar.readchar()
				if kb == "q":
						print("[exit program]")
						print "<pose_init>"	
						ser.write("@012c:T8000:T8000:T8000:T0000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000::::::T8000:T8000:T6800:T9800:T6800:T9800:T8000:T8000:T9800:T6800:T9800:T6800\n")
						print ser.readline(),
						rospy.sleep(3)

						print "<gain_off>"
						ser.write("P0000\n")
						print ser.readline(),

						break



