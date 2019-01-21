#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import math
from sensor_msgs.msg import *
from geometry_msgs.msg import *
from sobit_bringup.msg import *

#---palamater--------------------------------
D = 16	#2D=tread(車輪の幅)
T = 30

#---グローバル変数-----------------------------
motion = [0]*21
L_motion_cm = 0
R_motion_cm = 0
CMD_first_flag = True
CMD_LAST_TIME = rospy.Time()
serial_cmd = Serial_motion()


####[車輪の計算]-----------------------------------------------------------------------------------------
def cul_wheel(vel,ang,delta_T):
			global L_motion_cm, R_motion_cm, D
			
			print "[CUL_WHEEL]"
			print "vel:",vel 			#vel:速度[m/s]
			print "ang:",ang 			#ang:角速度[rad/s]
			print "time:",delta_T 	#time:単位時間[s]

			#左右車輪の速度の計算
			vel = vel * 100 #translate 'm' to 'cm' 
			L_motion_vel = (vel - ang * D)
			R_motion_vel = (vel + ang * D)

 			#左右車輪
			L_motion_cm += L_motion_vel * delta_T
			R_motion_cm += R_motion_vel * delta_T
			print "L_motion_cm:",L_motion_cm
			print "R_motion_cm:",R_motion_cm

			#シリアルパルス化
			motion[0] = '%04x' %(delta_T * 40)
			motion[1] = '%04x' %(32768 + L_motion_cm * 44)	#<L_wheel>
			motion[2] = '%04x' %(32768 - R_motion_cm * 44)		#<R_wheel>

			print "motion:",motion

			return motion


####[CMD_VEL CALLBACK]-------------------------------------------------------------------------------------
def callback2(cmd_vel):	
			global CMD_first_flag, CMD_LAST_TIME
			global serial_cmd

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
			
			serial_cmd.name = "CMD"
			serial_cmd.serial = "@"+motion[0]+":T"+motion[1]+":T"+motion[2]+"::::::::::::::::::::::::::::\n"

			print serial_cmd
			
			#シリアル信号の送信
			pub = rospy.Publisher('serial_msg', Serial_motion , queue_size=1)		#publisherの定義
			pub.publish(serial_cmd)


####[メイン関数]#################################################################################################################
if __name__ == '__main__':
			rospy.init_node('cmd_vel_listner')

			sub = rospy.Subscriber('sobit/cmd_vel', Twist, callback2)				#cmd_vel
			rospy.spin()

