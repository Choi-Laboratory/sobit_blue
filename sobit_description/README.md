HOW TO USE sobit_description

# launch
1. display.launch
		rvizを起動　ソビットのURDFモデルを表示させる

2. lidar.launch
		lidarセンサを起動　sensor_scanが出力されるようになる

3. robovie_maker.launch
		'rviz' + 'robovie_maker.py' + 'save_motion'を起動
		「joint state publisher」のスライダーを動かすことででSOBITを動かすことができる
		モーションの保存は「SAVEMOTION」で行う→motionに保存される
		

# text_controller
publishされたmotion_degをシリアル通信に変換し、送信する
1. ./sobit_description/sobit_controller

# send_motion
Robovie_makerで作成したモーションファイルの内容をmotion_deg型でpublishする(テスト用）
1. ./sobit_description/send_motion　
