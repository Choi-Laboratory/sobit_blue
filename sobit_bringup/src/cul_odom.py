#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import math
import time
from tf.msg import *
from numpy import *
from std_msgs.msg import *
from sensor_msgs.msg import *
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry

#======Initial Prameter======================
rR = 5			#右車輪半径  
rL = 5			#左車輪半径
T 	= 32.5		#Tread:車輪幅
PRp1 = 1408		#車輪1回転あたりのパルス(32cm*44)


#======global================================
rospy.init_node('cul_odom')
#車輪の位置パルス（前回）
LAST_L = 32768
LAST_R = 32768
LAST_T = rospy.Time.now()
#ロボットの自己位置（前回）
LAST_P_x = 0
LAST_P_y = 0
LAST_P_ang = 0

sobit_enc_twist = Twist()
odom = Odometry()

####talker########################################################################################################
def talker():
			sub = rospy.Subscriber('/sobit_enc', JointState, odom_callback) #Jointstateの読み込み
			#pub = rospy.Publisher('tf_static', tfMessage)	

			

####callback########################################################################################################
def odom_callback(sobit_enc):
			global LAST_L, LAST_R, LAST_T
			global LAST_P_x, LAST_P_y, LAST_P_ang
			
			global sobit_enc_twist

			print sobit_enc.position

			palse_L = 32768 + (sobit_enc.position[0] *180 /math.pi)*44
			palse_R = 32768 - (sobit_enc.position[1] *180 /math.pi)*44
			print "palse_L:", palse_L
			print "palse_R:", palse_R

			#print "LAST_T:", LAST_T

			print "T:", sobit_enc.header.stamp
			delta_T = sobit_enc.header.stamp - LAST_T
			delta_T_sec =  delta_T.to_sec()
			
			print "delta_T:", delta_T_sec

			#各車輪の角速度の計算
			Wl = (palse_L - LAST_L)/(PRp1 * delta_T_sec)
			Wr = (palse_R - LAST_R)/(PRp1 * delta_T_sec)
			#print "Wl:",Wl
			#print "Wr:",Wr

			#ロボットのcmd_velの計算
			vel = (rR/2*Wr) + (rL/2*Wl)
			ang = (rR/T*Wr) - (rL/T*Wl)
			print "Vel:",vel
			print "ang:",ang

			sobit_enc_twist.linear.x = vel
			sobit_enc_twist.angular.z = vel
			#print sobit_enc_twist

			#自己位置の計算
			place_x = LAST_P_x + (vel * math.cos(ang) * delta_T_sec)
			place_y = LAST_P_y + (vel * math.sin(ang) * delta_T_sec)
			place_ang = LAST_P_ang + (ang * delta_T_sec) 
			print "place_x	  :",place_x
			print "place_y	  :",place_y
			print "place_ang :",place_ang

			print odom
			odom.pose.pose.position.x = place_x
			odom.pose.pose.position.y = place_y
			odom.pose.pose.orientation.y = place_y

			#データの格納
			LAST_L = palse_L
			LAST_R = palse_R
			LAST_P_x = place_x
			LAST_P_y = place_y
			LAST_P_ang = place_ang
			LAST_T = sobit_enc.header.stamp


			print odom.pose.pose.position




####メイン関数#################################################################################################################
if __name__ == '__main__':
			talker()
			rospy.spin()




