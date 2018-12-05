#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import math
import time
from std_msgs.msg import *
from nav_msgs.msg import Odometry
from tf.msg import *
from sensor_msgs.msg import *
from geometry_msgs.msg import *
from numpy import *

#======Initial Prameter======================
D_RIGHT = 
D_LEFT = 
GR = 100.0 
PR =
TREAD = 32.5





def talker():
			rospy.init_node('cul_odom/tf_publisher')	
			sub = rospy.Subscriber('/sobit_enc_joint', JointState, odom_callback) #Jointstateの読み込み
			pub = rospy.Publisher('tf_static', tfMessage)	

			

####callback########################################################################################################
def odom_callback(sobit_enc):
			print sobit_enc

			left_enc = 32768 	+ (left_enc.position[0] *180 /3.14)*44
			right_enc = 32768 - (right_enc.position[1] *180 /3.14)*44
			print "left_enc:",+left_enc
			print "right_enc:",+right_enc

			#各車輪の角速度の計算
			left_wheel_radps = 
		




####メイン関数#################################################################################################################
if __name__ == '__main__':
			talker()
			
			
			

			rospy.spin()
