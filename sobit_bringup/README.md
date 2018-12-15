sobit_bringup
----------------------------------------------

1. sobit_motiondeg.launch
		topic「motion_deg」をシリアル通信形式に変換して送受信する。
		for OpenCampus

2. lidar.launch 
 		LIDARセンサを起動する
		sensor_scanが出力される

3. sobit_wheel.launch
		SOBITの足回りの起動。
		トピック「cmd_vel（Twist型）」をsubscribeして車輪を制御する。
		エンコーダによる各関節のpositionを「sobit_enc(JointState型)でpublishする

4. sobit_minimal.launch
		足回りと上半身の起動。
		トピック「cmd_vel(Twist型)」による車輪制御とトピック「joint_state(JointState型)」による上半身関節の制御。		
