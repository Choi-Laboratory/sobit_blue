#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import sys
import roslib.packages
from sensor_msgs.msg import *
from geometry_msgs.msg import *

file_path = roslib.packages.get_pkg_dir('sobit_test') + "/output/"
in_file = open(file_path + 'in_state.txt', 'w')		#書き込みモードでオープン
first_flag = True
first_sec = 0

def callback(in_jointstate):
	global first_flag,first_sec
	print in_jointstate

	if	first_flag == True:
		first_sec = in_jointstate.header.stamp.secs
		first_flag = False

	in_state = str(in_jointstate.position[2])
	in_time_sec = str(in_jointstate.header.stamp.secs)
	in_time_sec2 = str(in_jointstate.header.stamp.secs - first_sec)
	in_time_nsec = str(in_jointstate.header.stamp.nsecs)
	in_time = in_time_sec + '.' + in_time_nsec

	print in_state
	print in_time_sec
	print in_time_nsec
	print in_time

	#in_file.write("in_state:")
	in_file.write(in_state)
	#in_file.write("\tsec:")
	#in_file.write(in_time_sec)
	#in_file.write("\tnsec:")
	#in_file.write(in_time_nsec)
	in_file.write("\t")
	in_file.write(in_time)
	in_file.write("\n")
	

if __name__ == '__main__':
	rospy.init_node('joint_test')

	print "[in_state]"
	in_file.write("in_state")
	in_file.write("\ttime\n")

	sub = rospy.Subscriber('/joint_states', JointState, callback)	

	rospy.spin()

	print "exit"
	in_file.close()
	
