sobit_serial
================

シリアル通信制御テストPKG

シリアル通信 to VSRC003

モーションの送信
-----------------------
1：	モーションタイム	@0000(16進数4桁）
	%04x(1ms/25)

2：	各関節ポジション	C0000(16進数4桁)	
	CH)	NAME)					安全な可動域:rad）		10進数化計算）
	CH1	L_WHEEL				---						32768+(deg*44)
	CH2	R_WHEEL				---						32768-(deg*44)
	CH3	L_sholder_roll		上+3.14					32768+(deg*97)
	CH4	L_shouler_pitch	前+3.14	後-1.57
	CH5	L_elbow_yaw			外+1.57	内-3.14
	CH6	R_elbow_pitch		上+3.14	下-0.30
	CH7	R_sholder_roll		上+3.14
	CH8	R_shouler_pitch	前+3.14	後-1.57
	CH9	R_elbow_yaw			外+1.57	内-3.14
	CH10	R_elbow_pitch		上+3.14	下-0.30
	CH11	neck_pitch			上+0.51	下-0.51
	CH12	neck_yaw				左+0.51	右-0.51
	CH13	neck_roll			右+1.57	左-1.57
	CH15	no use
	CH16	no use
	CH17	no use
	CH18	no use
	CH19	no use
	CH20	L_hand_wrist		内+1.57	外-1.57
	CH21	L_hand_thumb		開+1.57	閉-1.57
	CH22	L_hand_index		閉-3.14
	CH23	L_hand_mid			閉-3.14
	CH24	L_hand_ring			閉-3.14
	CH25	L_hand_pinky		閉-3.14
	CH26	R_hand_wrist		閉+3.14	→握手用
	CH27	R_hand_thumb		開+1.57	閉-1.57
	CH28	R_hand_index		閉-3.14
	CH29	R_hand_mid			閉-3.14
	CH30	R_hand_ring			閉-3.14
	CH31	R_hand_pinky		閉-3.14

