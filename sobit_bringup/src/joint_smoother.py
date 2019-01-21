#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import *
from geometry_msgs.msg import *

MAX_RAD = 0.01	#1フレーム間の最大変化量

pub = rospy.Publisher('sobit/joint_states', JointState , queue_size=10)

#送信するjointを格納する変数
push_joint = JointState()
push_joint.name =["L_wheel","R_wheel","L_shoulder_roll","L_shoulder_pitch","L_elbow_yaw","L_shoulder_pitch","R_shoulder_roll","R_shoulder_pitch","R_elbow_yaw","R_elbow_pitch","neck_pitch","neck_roll","neck_yaw","L_hand_twist","L_hand_thumb","L_hand_index","L_hand_mid","L_hand_ring","L_hand_pinky","R_hand_twist"]
push_joint.position = [0.0, 0.0, 0.0, -0.0003526000000000362, -0.00011850000000013239, -3.199999999997649e-05, 0.0, -0.0003526000000000362, -0.00011850000000013239, -3.199999999997649e-05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

#前フレームのjointを格納する変数（default:初期位置)
BEFORE_POSITION = [0.0, 0.0, 0.0, -0.0003526000000000362, -0.00011850000000013239, -3.199999999997649e-05, 0.0, -0.0003526000000000362, -0.00011850000000013239, -3.199999999997649e-05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


### なめら化処理　#############################################################
def smoother(GOAL):
	global BEFORE_POSITION
	global MAX_RAD

	#print "BEFORE:",BEFORE_POSITION
	print "\n[なめら化判定]"

	#なめら化処理の根幹部分
	for i in range(0,20):
		if GOAL.position[i] - BEFORE_POSITION[i] == 0:	
				#jointが前フレームと変化なし
				print i,"\t:A"
				push_joint.position[i] = GOAL.position[i]
			
		elif GOAL.position[i] - BEFORE_POSITION[i] > MAX_RAD:
				#jointの値が前フレームから最大変化量より大きい	
				print i,"\t:B"
				push_joint.position[i] = BEFORE_POSITION[i] + MAX_RAD
		
		elif BEFORE_POSITION[i] - GOAL.position[i] > MAX_RAD:
				#jointの値が前フレームから最大変化量より小さい	
				print i,"\t:C"
				push_joint.position[i] = BEFORE_POSITION[i] - MAX_RAD

		else:
				#jointの値が前フレームより最大変化量以下の変化
				print i,"\t:D"
				push_joint.position[i] = GOAL.position[i]

		BEFORE_POSITION[i] = push_joint.position[i]

	#time stampの付与
	now = rospy.get_rostime()
	push_joint.header.seq = GOAL.header.seq
	push_joint.header.stamp.secs = now.secs
	push_joint.header.stamp.nsecs = now.nsecs


	#print "push:",push_joint.position
	return push_joint
		

### callback　#############################################################
def callback(joint):

	print "\n[送られてきたジョイント角度]"
	for i in range(0,20):
		print joint.name[i],":", joint.position[i]

	#なめら化処理
	push_joint = smoother(joint)

	print "\n[送信するジョイント]"
	print "push:",push_joint

	#加工したジョイントの送信
	pub.publish(push_joint)


### joint_statesの読み込み　#############################################################
def joint_read():
	rospy.init_node('joint_state_publisher', anonymous=True)
	sub = rospy.Subscriber('joint_states', JointState, callback)
	rospy.spin()


### main関数　#############################################################
if __name__ == '__main__':
    joint_read()



