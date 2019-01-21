#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import math
import time
import roslib.packages
from numpy import *
from tf.msg import *
from std_msgs.msg import *
from sensor_msgs.msg import *
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry

cnow = time.ctime()
cnvtime = time.strptime(cnow)
ex_time = time.strftime("%Y%m%d %H%M",cnvtime)

file_path = roslib.packages.get_pkg_dir('sobit_test') + "/output/cmd_vel/"
out_file = open(file_path + 'cmd_vel_test' + ex_time + '.txt', 'w')		#書き込みモードでオープン


#======Initial Prameter======================
rR = 5			#右車輪半径  
rL = 5			#左車輪半径
T 	= 32.5		#Tread:車輪幅

#======global================================
rospy.init_node('cmd_vel_test')
#車輪の位置パルス
LAST_L = 32768
LAST_R = 32768
LAST_T = rospy.Time.now()
#ロボットの自己位置
LAST_P_x = 0
LAST_P_y = 0
LAST_P_ang = 0

first_flag = True
first_time_global = rospy.Time.now()


sobit_enc_twist = Twist()

####データの送信（ファイル書き込み）###################################
def file_push():
			global first_flag, first_time_global

			if first_flag == True:
				first_time = str(first_time_global)
				out_file.write("first_time:")
				out_file.write(first_time)
				out_file.write("\n")
				out_file.write("time\tvel\tang\tX  \tY  \tang\t\n")
				first_flag = False

			vel = str(VEL)
			ang = str(ANG)
			x = str(LAST_P_x)
			y = str(LAST_P_y)
			w = str(LAST_P_ang)
			time = LAST_T - first_time_global
			time = time.to_sec()
			time = str(time)
			
			out_file.write(time)
			out_file.write("\t")
			out_file.write(vel)
			out_file.write("\t")
			out_file.write(ang)
			out_file.write("\t")
			out_file.write(x)
			out_file.write("\t")
			out_file.write(y)
			out_file.write("\t")
			out_file.write(w)
			out_file.write("\n")
			

def talker():
			sub = rospy.Subscriber('sobit/cmd_vel', Twist, odom_callback) #Jointstateの読み込み
			#pub = rospy.Publisher('tf_static', tfMessage)	


####callback########################################################################################################
def odom_callback(cmd_vel):
			global LAST_P_x, LAST_P_y, LAST_P_ang, LAST_T, VEL, ANG

			print "\n[cmd_vel]"

			#微小時間の計算
			now = rospy.Time.now()
			delta_T = now - LAST_T
			delta_T_sec = delta_T.to_sec()
			#delta_T_sec = 0.1
			print "delta_T:", delta_T_sec

			#print "\n",cmd_vel
			#print "LAST_T:", LAST
			
			vel = cmd_vel.linear.x
			ang = cmd_vel.angular.z
			print "Vel:",vel
			print "ang:",ang

			#自己位置の計算
			place_ang = LAST_P_ang + (ang * delta_T_sec) 
			place_x = LAST_P_x + (vel * math.cos(place_ang) * delta_T_sec)
			place_y = LAST_P_y + (vel * math.sin(place_ang) * delta_T_sec)
			
			print "place_x	  :",place_x
			print "place_y	  :",place_y
			print "place_ang :",place_ang

			#データの格納
			VEL = vel
			ANG = ang
			LAST_P_x = place_x
			LAST_P_y = place_y
			LAST_P_ang = place_ang
			LAST_T = now

			#データの送信（ファイル書き込み）
			file_push()

			

####メイン関数#################################################################################################################
if __name__ == '__main__':
			out_file.write("cmd_vel_test\n")
			

			talker()
			rospy.spin()



