#!/usr/bin/env python
# -*- coding: utf-8 -*-

#このプログラムの説明：車輪と上半身関節の命令を個々の時間で分けて送ることができるかの実験

import serial
import rospy
from sensor_msgs.msg import *

ser=serial.Serial(
  	port = '/dev/vsrc',
   	baudrate = 115200,
 	 	parity = serial.PARITY_NONE, 
 	 	bytesize = serial.EIGHTBITS,
 	 	stopbits = serial.STOPBITS_ONE,
   	timeout = None,
   	xonxoff = 0,
   	rtscts = 0,
#   interCharTimeout = None
)

joint_name =  ["","L_wheel","R_wheel","L_shoulder_roll","L_shoulder_pitch","L_elbow_yaw","L_shoulder_pitch", "R_shoulder_roll","R_shoulder_pitch","R_elbow_yaw","R_elbow_pitch", "neck_pitch","neck_roll\t","neck_yaw\t","nouse","nouse","nouse","nouse","nouse","L_hand_yaw","L_hand_thumb","L_hand_index","L_hand_mid","L_hand_ring","L_hand_pinky","R_hand_yaw","R_hand_thumb","R_hand_index","R_hand_mid","R_hand_ring","R_hand_pinky"]


L_motion_deg = 0
R_motion_deg = 0

while True:
	#try:
		print("\n1.pose_init  2.R  3.get_enc  4.gain_on  5.gain_off  6.motion 0.exit")
		command = input("select>>")
		
		if command == 1: #<pose_init>
			ser.write("@00c8:T8000:T8000:T8000:T0000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000:T8000::::::T8000:T8000:T6800:T9800:T6800:T9800:T8000:T8000:T9800:T6800:T9800:T6800\n")
			print ser.readline(),

		elif command == 2: #<R>
			ser.write("R\n")
			print ser.readline(),

		elif command == 3: #<get_enc>
			ser.write(":Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx::::::T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx:T8000:Cxxxx:Cxxxx:Cxxxx:Cxxxx:Cxxxx\n");
			str = ser.readline(),
			print str[0]
			position_enc = str[0].split(";")
			
			#print str[0].split(";")
			#print "left_wheel:",position_list[1]
			
			
			for i in range(1,31):
				position_enc[i] = position_enc[i][1:]				#最初の文字(C)削除
				if len(position_enc[i]) != 0:
					position_enc[i] = int(position_enc[i],16)		#16進数→10進数
				else:
					pass

			#print position_enc
			position_enc2 = [0]*30
			#print position_enc[0]

			#cm変換
			position_enc2[1] = (position_enc[1] - 32768)/44 
			position_enc2[2] = (position_enc[2] - 32768)/44		
			position_enc2[3] = (position_enc[3] - 32768)/97		#<L_shoulder_roll>
			#position_enc[4] = (position_enc[4] - 32768)/86		#<L_shoulder_pitch>
			position_enc2[5] = (position_enc[5] - 32768)/58		#<L_elbow_yaw>
			position_enc2[6] = (position_enc[6] - 32768)/105		#<L_elbow_pitch>
			position_enc2[7] = (position_enc[7] - 32768)/97		#<R_shoulder_roll>
			position_enc2[8] = (position_enc[8] - 32768)/86		#<R_shoulder_pitch>
			position_enc2[9] = (position_enc[9] - 32768)/58		#<R_elbow_yaw>
			position_enc2[10] = (position_enc[10] - 32768)/105	#<R_elbow_pitch>
			position_enc2[11] = (position_enc[11] - 32768)/110	#<neck_pitch>
			position_enc2[12] = (position_enc[12] - 32768)/112	#<neck_roll>	
			position_enc2[13] = (position_enc[13] - 32768)/246	#<neck yaw>
			position_enc2[19] = (position_enc[19] - 32768)/91	#<L_hand_twist>
			position_enc2[22] = (position_enc[20] - 32768)/91	#<L_hand_thumb>
			position_enc2[21] = (position_enc[21] - 26624)/68	#<L_hand_index>
			position_enc2[22] = (position_enc[22] - 38912)/68	#<L_hand_middle>
			position_enc2[23] = (position_enc[23] - 26624)/68	#<L_hand_ring>
			position_enc2[24] = (position_enc[24] - 38912)/68	#<L_hand_index>	
			position_enc2[25] = (position_enc[25] - 32768)/91	#<R_hand_twist>

			#print position_enc

			for i in range(1,3):
				print  '%2d'%i,")", joint_name[i],"\t:", position_enc[i],"\t:", position_enc2[i]

		elif command == 4: #<gain_on>
			ser.write(":P0100:P0100:P0040:P0080:P0045:P0040:P0040:P0080:P0045:P0040:P0080:P0200:P0016::::::P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001:P0001\n")

			print ser.readline(),

		elif command == 5: #<gain_off>
			ser.write("P0000\n")
			print ser.readline(),

		elif command == 6: #<motion>
			print "\n<move wheel>"

			motion_type = input("1:panzer vor! 2:RIGHT! 3:LEFT! 4:reverse! 5:cancel>")
			if motion_type == 1:
					motion_in = input("distance of ahead!>")
					L_motion_deg += motion_in
					R_motion_deg += motion_in
					motion_time = motion_in * 0.5

			elif motion_type == 2:
					rad = input("rad of turn right!>")
					L_motion_deg += rad * 0.35
					R_motion_deg -= rad * 0.35
					motion_time = rad * 0.6

			elif motion_type == 3:
					rad = input("rad of turn left!>")
					L_motion_deg -= rad * 0.35
					R_motion_deg += rad * 0.35
					motion_time = rad * 0.6

			elif motion_type == 4:
					motion_in = input("distance of reverse!>")
					L_motion_deg -= motion_in
					R_motion_deg -= motion_in
					motion_time = motion_in * 0.8		

			elif motion_type == 5:
					break

			else: break

			print "L_motion_deg:", L_motion_deg
			print "R_motion_deg:", R_motion_deg
			print "motion_time :", motion_time

			#L_motion_deg = input("L:take in(-180~180)>")
			#R_motion_deg = input("R:take in(-180~180)>")
			
			L_wheel = 32768 + L_motion_deg * 52
			R_wheel = 32768 - R_motion_deg * 52

			print "L_wheel:", L_wheel
			print "R_wheel:", R_wheel

			L_wheel = '%x' % L_wheel
			R_wheel = '%x' % R_wheel
				
			#culculate motion_time
			motion_time *= 40
			time_16 = '%04x' %(motion_time)
			print time_16

			#add left_shoulder_roll
			L_shoulder_roll_deg = input("left_shoulder_roll_deg>")
			motion_time_upper = input("motion_time>")

			L_shoulder_roll = '%04x' %(32768 + L_shoulder_roll_deg * 97)		
			motion_time_upper = '%04x' %(motion_time_upper * 40)

			print "L_shoulder_roll:",L_shoulder_roll
			print "motion_time:",motion_time_upper

			#check motion[L&R WHEEL]
			print "motion_L&R_wheel"
			ser.write("@"+time_16+":T"+L_wheel+":T"+R_wheel+"::::::::::::::::::::::::::::\n")
			print ser.readline(),

			rospy.sleep(0.1)

			#check motion[L_shoulder_roll]
			print "motion_L_shulder_roll"
			ser.write("@"+motion_time_upper+":::T"+L_shoulder_roll+":::::::::::::::::::::::::::\n")
			print ser.readline(),


		elif command == 0: 
			ser.close() 
			break

		elif command == "":
			ser.close()
			break

		else: 
			ser.close() 
			break

	
	#except:
		#print "except"
		#break

