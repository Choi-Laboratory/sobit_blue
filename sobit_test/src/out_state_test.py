#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import sys
import roslib.packages
from sensor_msgs.msg import *
from geometry_msgs.msg import *

file_path = roslib.packages.get_pkg_dir('sobit_test') + "/output/"
out_file = open(file_path + 'enc_state.txt', 'w')		#書き込みモードでオープン
first_flag = True
first_sec = 0

def callback(enc):
	global first_flag,first_sec
	print enc

	if	first_flag == True:
		first_sec = enc.header.stamp.secs
		first_flag = False

	
	in_state = str(enc.position[2])
	in_time_sec = str(enc.header.stamp.secs)
	in_time_sec2 = str(enc.header.stamp.secs - first_sec)
	in_time_nsec = str(enc.header.stamp.nsecs)
	in_time = in_time_sec + '.' + in_time_nsec
	
	print in_state
	print in_time_sec
	print in_time_nsec
	print in_time

	#out_file.write("enc_state:")
	out_file.write(in_state)
	#out_file.write("\tsec:")
	#out_file.write(in_time_sec)
	#out_file.write("\tnsec:")
	#out_file.write(in_time_nsec)
	out_file.write("\t")
	out_file.write(in_time)
	out_file.write("\n")

if __name__ == '__main__':
	rospy.init_node('joint_test')
	
	print "[enc_state]"
	out_file.write("enc_state")
	out_file.write("\ttime\n")
	sub = rospy.Subscriber('/sobit_enc', JointState, callback)	

	rospy.spin()

	print "exit"
	out_file.close()
