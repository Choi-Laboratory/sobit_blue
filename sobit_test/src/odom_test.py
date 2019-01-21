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

now = time.ctime()
cnvtime = time.strptime(now)
ex_time = time.strftime("%Y%m%d %H%M",cnvtime)

file_path = roslib.packages.get_pkg_dir('sobit_test') + "/output/odom/"
out_file = open(file_path + 'cul_odom_test'+ ex_time +'.txt', 'w')		#書き込みモードでオープン


#======Initial Prameter======================
rR = 0.05		#右車輪半径  
rL = 0.05		#左車輪半径
T 	= 0.325		#Tread:車輪幅[m]
PRp1 = 1452		#車輪1回転あたりのパルス(31.4cm*44=1381,32*44=1408,33*44=1452)



#======global================================
rospy.init_node('cul_odom')
#車輪の位置パルス
LAST_L = 32768
LAST_R = 32768
LAST_T = rospy.Time.now()
#車輪の角速度
LAST_Wl = 0
LAST_Wr = 0
#ロボットの速度
VEL = 0
ANG = 0
#ロボットの自己位置
LAST_P_x = 0
LAST_P_y = 0
LAST_P_ang = 0

first_flag = True
first_time_global = rospy.Time.now()
sobit_enc_twist = Twist()

#---データの送信（ファイル書き込み）----------------------------------------			
def file_push():
			global first_flag, first_time_global
			
			#print "LAST_T:",LAST_T

			if first_flag == True:
				first_time = str(first_time_global)
				out_file.write("first_time:")
				out_file.write(first_time)
				out_file.write("\n")
				out_file.write("time    \tvel \tang \tX  \tY  \tang \tWl  \tWr\n")
				first_flag = False

			time = LAST_T - first_time_global
			time = time.to_sec()
			t = str(time)

			vel = str(VEL)
			ang = str(ANG)
			x = str(LAST_P_x)
			y = str(LAST_P_y)
			w = str(LAST_P_ang)
			wl = str(LAST_Wl)
			wr = str(LAST_Wr)
			out_file.write(t)
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
			out_file.write("\t")
			out_file.write(wl)
			out_file.write("\t")
			out_file.write(wr)
			out_file.write("\n")
			

def talker():
			sub = rospy.Subscriber('/sobit_enc', JointState, odom_callback) #Jointstateの読み込み
			#pub = rospy.Publisher('tf_static', tfMessage)	


####callback########################################################################################################
def odom_callback(sobit_enc):
			global LAST_L, LAST_R, LAST_T, VEL, ANG
			global LAST_P_x, LAST_P_y, LAST_P_ang, LAST_Wl, LAST_Wr
			
			global sobit_enc_twist

			print "\n",sobit_enc.position

			#各車輪のパルス値の計算
			palse_L = 32768 + (sobit_enc.position[0] *44)
			palse_R = 32768 + (sobit_enc.position[1] *44)
			#print "palse_L:", palse_L
			#print "palse_R:", palse_R

			palse_L = int(palse_L)
			palse_R = int(palse_R)
			#print "palse_L:", palse_L
			#print "palse_R:", palse_R

			L = (palse_L - 32768)/44
			R = (32768 - palse_R)/44
			#print "L:", L
			#print "R:", R

			#微小時間(delta_T)の計算
			#print "T:", sobit_enc.header.stamp
			#print "LAST_T:", LAST_T
			delta_T = sobit_enc.header.stamp - LAST_T
			delta_T_sec =  delta_T.to_sec()
			#delta_T_sec = 0.1	
			print "delta_T:", delta_T_sec

			#各車輪の角速度の計算
			#print "LAST_L:",LAST_L
			#print "LAST_R:",LAST_R
			palse_diff_L = palse_L - LAST_L
			palse_diff_R = LAST_R - palse_R
			#print "PALSE_diff_L:", palse_diff_L
			#print "PALSE_diff_R:", palse_diff_R
			Wl = (palse_diff_L)/(PRp1 * delta_T_sec)*2*math.pi
			Wr = (palse_diff_R)/(PRp1 * delta_T_sec)*2*math.pi
			#print "Wl:",Wl
			#print "Wr:",Wr

			#ロボットのcmd_velの計算
			vel = (rR/2*Wr) + (rL/2*Wl)
			ang = (rR/T*Wr) - (rL/T*Wl)
			print "Vel:",vel
			print "ang:",ang

			sobit_enc_twist.linear.x = vel
			sobit_enc_twist.angular.z = ang
			#print sobit_enc_twist

			#自己位置の計算
			place_ang = LAST_P_ang + (ang * delta_T_sec) 
			place_x = LAST_P_x + (vel * math.cos(place_ang) * delta_T_sec)
			place_y = LAST_P_y + (vel * math.sin(place_ang) * delta_T_sec)
			
			print "place_x	  :",place_x
			print "place_y	  :",place_y
			print "place_ang :",place_ang

			#データの格納
			LAST_Wl = Wl
			LAST_Wr = Wr
			LAST_L = palse_L
			LAST_R = palse_R
			VEL = vel
			ANG = ang
			LAST_P_x = place_x
			LAST_P_y = place_y
			LAST_P_ang = place_ang
			LAST_T = sobit_enc.header.stamp

			file_push()

			

####メイン関数#################################################################################################################
if __name__ == '__main__':
			out_file.write("odom_test\n")

			talker()
			rospy.spin()



