# -*- coding:utf-8 -*-
from itertools import zip_longest
import pyvisa as visa
import time
import numpy as np
import sys

class E5270_twin:
    # SMUの初期設定，測定プログラムのSMU内部プログラム・メモリへの書き込みを行う
    # 測定部分はプログラム・メモリへの書き込み不可のため，pythonで制御する
    def __init__(self,GPIB0='GPIB0::9::INSTR',GPIB1='GPIB2::17::INSTR'):
        self.rm = visa.ResourceManager()
        time.sleep(0.001)
        self.SMU1 = self.rm.open_resource(str(GPIB0))
        time.sleep(0.001)
        self.SMU1.write("*RST")
        time.sleep(0.001)
        print (self.SMU1.query("*IDN?"))
        self.SMU2 = self.rm.open_resource(str(GPIB1))
        time.sleep(0.001)
        self.SMU2.write("*RST")
        time.sleep(0.001)
        print (self.SMU2.query("*IDN?"))
        self.SMU1.write("*RST")
        self.SMU2.write("*RST")
        self.SMU1.timeout=1000000
        self.SMU2.timeout=1000000

    def setting(self,ch=[i for i in range(1,17)],mparam=['I' for i in range(1,17)],mode='spot'):
        ch1 = [c for c in ch if c<9 and c>0]
        mp1 = [mparam[i] for i in range(len(mparam)) if i < len(ch1)]
        str_ch1 = str(ch1).replace('[','').replace(']','')
        ch2 = [c-8 for c in ch if c>=9]
        mp2 = [mparam[i] for i in range(len(mparam)) if i >= len(ch1)]
        str_ch2 = str(ch2).replace('[','').replace(']','')

        #SMUの設定
        self.SMU1.write("CN "+str(str_ch1))
        self.SMU1.write('FMT 5,0')
        # ADCの設定AVとAITはどちらか一方（どちらでもよい？）
        self.SMU1.write('AV 4,1')
        #self.SMU1.write('AIT 0,4')
        # 測定データに時間データを追加（測定開始時にタイマー0にする必要あり）
        self.SMU1.write('TSC 1')
        self.SMU1.write('BC')
        self.SMU1.write('FL 0')
        self.SMU1.write('WAT 1,0,0.001') # 1msかけて出力電圧を変更
        self.SMU1.write('WAT 2,0,0.002') # 2ms測定まで待つ（内1msは出力電圧変更）


        if mode == 'spot':
            self.SMU1.write('MM 1,'+str(str_ch1))
        elif mode == 'sweep':
            self.SMU1.write('MM 16,'+str(str_ch1))
        for c1, mp in zip(ch1,mp1):
            if mp=='I': # 電流測定を指定
                self.SMU1.write('CMM '+str(c1)+',1')
                self.SMU1.write('RI '+str(c1)+',11')# 11: 1nA limited auto
            elif mp=='V': # 電圧測定を指定
                self.SMU1.write('CMM '+str(c1)+',2')
                self.SMU1.write('RV '+str(c1)+',0')
            elif mp=='IV': # 電圧印加:電流測定，電流印加:電圧測定
                pass
        if len(ch2) == 0 and len(mp2) == 0:
            return
        self.SMU2.write("CN "+str(str_ch2))
        self.SMU2.write('FMT 5,0')
        # ADCの設定AVとAITはどちらか一方（どちらでもよい？）
        self.SMU2.write('AV 4,1')
        #self.SMU2.write('AIT 0,4')
        # 測定データに時間データを追加（測定開始時にタイマー0にする必要あり）
        self.SMU2.write('TSC 1')
        self.SMU2.write('BC')
        self.SMU2.write('FL 0')
        self.SMU2.write('WAT 1,0,0.001') # 出力電圧を変更する際に10msec待つ
        self.SMU2.write('WAT 2,0,0.002') # 出力電圧を変更する際に1msec待つ
        if mode == 'spot':
            self.SMU2.write('MM 1,'+str(str_ch2))
        elif mode == 'sweep':
            self.SMU2.write('MM 16,'+str(str_ch2))
        for c2, mp in zip(ch2, mp2):
            if mp=='I': # 電流測定を指定
                self.SMU2.write('CMM '+str(c2)+',1')
                self.SMU2.write('RI '+str(c2)+',11')#11: 1nA limited auto
            elif mp=='V': # 電流測定を指定
                self.SMU2.write('CMM '+str(c2)+',2')
                self.SMU2.write('RV '+str(c2)+',0')
            elif mp=='IV': # 電圧印加:電流測定，電流印加:電圧測定
                pass
        self.SMU1.write('DZ')
        self.SMU2.write('DZ')

#sweep_param=[0.1*v for v in range(0,31)]
#[0.1, 0.2, ..., 3.0]
    def IVmeas_spot(self,CHIP_set=[[1,2,3,4,5]],none_ch=[],NP=1,Vdd=0,sweep_param=[0.1*v for v in range(0,31)],icomp=1.0e-2,vcomp=10):
        # S: GND, G: sweep, D: Vdd
        # 3端子素子の測定用，1端子の電圧をスイープして各端子の電流を測定
        # 測定プログラムをSMUのプログラム・メモリに書き込む
        HV_set  = []
        Y3_set  = []
        V5_set  = []
        V3_set  = []
        V0_set  = []
        for CHIP in CHIP_set:
            HV,Y3,V5,V3,V0=CHIP
            if type(HV)==int:
                HV_set.append(HV)
            if type(Y3)==int:
                Y3_set.append(Y3)
            if type(V5)==int:
                V5_set.append(V5)
            if type(V3)==int:
                V3_set.append(V3)
            if type(V3)==int:
                V0_set.append(V0)

        print (HV_set)
        print (Y3_set)
        print (V5_set)
        print (V3_set)
        print (V0_set)
        HV_1 = [hv for hv in HV_set if hv<9 and hv>0]
        Y3_1 = [y3 for y3 in Y3_set if y3<9 and y3>0]
        V5_1 = [v5 for v5 in V5_set if v5<9 and v5>0]
        V3_1 = [v3 for v3 in V3_set if v3<9 and v3>0]
        V0_1 = [v0 for v0 in V0_set if v0<9 and v0>0]
        invalid1 = [i for i in none_ch if i<9]
        invalid2 = [i-8 for i in none_ch if i>=9]
        print (invalid1)
        print (invalid2)
        # S,D,Bに電位を与える（これらの3端子は掃引しない）
        self.SMU1.write('ST 1')
        print ('***** SMU1 *****')
        print ('ST 1')
        for v0 in V0_1:
            self.SMU1.write('DV '+str(v0)+',0,'+str(0)+','+str(icomp))#0Vを印加
            print ('DV '+str(v0)+',0,'+str(0)+','+str(icomp))
        for v3 in V3_1:
            self.SMU1.write('DV '+str(v3)+',0,'+str(3.3)+','+str(icomp))#3.3Vを印加
            print ('DV '+str(v3)+',0,'+str(3.3)+','+str(icomp))
        for v5 in V5_1:
            self.SMU1.write('DV '+str(v5)+',0,'+str(5.3)+','+str(icomp))#5.3Vを印加
            print ('DV '+str(v5)+',0,'+str(5.3)+','+str(icomp))
        for y3 in Y3_1:
            self.SMU1.write('DV '+str(y3)+',0,'+str(8.6)+','+str(icomp))#8.6Vを印加
            print ('DV '+str(y3)+',0,'+str(8.6)+','+str(icomp))
        for i in invalid1:
            self.SMU1.write('DI '+str(i)+',0,'+str(0)+','+str(vcomp))
            print ('DI '+str(i)+',0,'+str(0)+','+str(vcomp))
        self.SMU1.write('END')
        print ('***** SMU1 *****')
        # 電圧掃引
        # この部分に測定命令を組み込む場合は，測定終了待ちの命令が必要
        # 現状，都合の良い命令がイマイチ見つからない．．．
        # Vgはsweep_pramの値(全部同じ値にてsleepで回す(ここではWAT?))
        for Vg,i in zip(sweep_param,range(len(sweep_param))): #sweep_pramごとに回す
            print ('***** SMU1 *****')
            print ('ST {}'.format(i+2))
            self.SMU1.write('ST {}'.format(i+2))
            for hv in HV_1:#G1の要素ごとに回す（今回は１つだけなので1回だけ）
                self.SMU1.write('DV '+str(hv)+',0,'+str(NP*Vg)+','+str(icomp))
                print ('DV '+str(hv)+',0,'+str(NP*Vg)+','+str(icomp))#DV：一定電圧を印加
            self.SMU1.write('END')




#階段波掃引測定を使ったサンプリング測定
#変更したもの
#SGDBの順番注意
#TODOもーちょい分かりやすくする
    def IVmeas_sweep(self,SGDB_set=[[2,3,1,4]],none_ch=[],NP=1,Vdd=3.0,vstart=3.0,vend=3.0,vstep=0.1,icomp=1.0e-3,vcomp=15,tot_step=1000):
        # S: GND, G: sweep, D: GND　B：GND
        # 4端子素子の測定用，1端子の電圧をスイープして各端子の電流を測定
        # 測定プログラムをSMUのプログラム・メモリに書き込む
        # output_wait: 出力変更後測定開始までの待ち時間，meas_wait: 測定開始後出力変更までの待ち時間
        output_wait, meas_wait = 50e-3, 50e-3 #100msごとに測定する
        #tot_step = int((vend-vstart)/vstep+1)
        #tot_step = int(100)
        print (SGDB_set)
        S_set, G_set, D_set, B_set  = [], [], [], []
        for SGDB in SGDB_set:
            S,G,D,B=SGDB
            if type(S)==int:
                S_set.append(S)
            if type(G)==int:
                G_set.append(G)
            if type(D)==int:
                D_set.append(D)
            if type(D)==int:
                B_set.append(B)
        S1 = [s for s in S_set if s<9 and s>0]
        S2 = [s-8 for s in S_set if s>=9]
        G1 = [g for g in G_set if g<9 and g>0]
        G2 = [g-8 for g in G_set if g>=9]
        D1 = [d for d in D_set if d<9 and d>0]
        D2 = [d-8 for d in D_set if d>=9]
        B1 = [b for b in B_set if b<9 and b>0]
        B2 = [b-8 for b in B_set if b>=9]
        #ここ
        invalid1 = [i for i in none_ch if i<9]
        invalid2 = [i-8 for i in none_ch if i>=9]
        #チャネル番号の指定(8以下だけ使うようにする)
        print (S1,G1,D1,B1,invalid1) 
        print (S2,G2,D2,B2,invalid2)

        self.SMU1.write('ST 1') #プログラムの開始を意味する。１はプログラム番号

        #階段波掃引測定の設定
        #WT hold,delay[,Sdelay[,Tdelay[,Mdelay]]]
        #hold：ホールド時間(s)。掃引測定開始から第一掃引ステップにおけるディレイ時間開始までの時間
        #delay：ディレイ時間(s)。ステップ出力開始から測定開始までの時間
        #sdelay：ステップディレイ時間。ステップ測定開始から次のステップ出力開始までの時間
        self.SMU1.write('WT 0,{0},{1}'.format(output_wait,meas_wait)) 

        print ('***** Measurement program is shown below *****')
        print ('WT 0,{0},{1}'.format(output_wait,meas_wait))


        #実行の方法が分かれば行ける気がする
        #一つ目のG1の時は、掃引の設定をして、2つ目以降のＧ１に関してはその設定を再利用する
        #今回する実験ではG1の要素は1つのみなので、ifの下りは必要ない（sとかと同じ方法でよい）
        #
        for g in G1:
            self.SMU1.write('WV '+str(g)+','+'1,0,'+str(NP*vstart)+','+str(NP*vend)+','+str(tot_step)+','+str(icomp))
                #WV：階段波電圧掃引源とそのパラメータの設定
                #WV chnum,mode,range,start,stop,step[,Icomp[,Pcomp]]
                #chnum：掃引出力チャネル番号
                #mode：掃引モード。１：リニア掃引　２：ログ掃引　３：リニア掃引ダブル　４：ログ掃引ダブル
                #range：table4.4参照　0：オート
                #start,stop：スタート、ストップ電圧　table4.6参照
                #step：掃引ステップ数　1~1001 
                #Icomp：電流コンプライアンス
                #Pcomp：パワーコンプライアンス　省略可
            print ('WV '+str(g)+','+'1,0,'+str(NP*vstart)+','+str(NP*vend)+','+str(tot_step)+','+str(icomp))
        for s in S1:
            self.SMU1.write('DV '+str(s)+',0,'+str(0)+','+str(icomp)) #０Vを印加
            #DV：指定されたチャネルから電圧を出力
            #DV chnum,vrange,voltage[,Icomp[,comp_polarity[,irange]]
            #chnum：チャネル番号
            #vrange：レンジングタイプ。table4.4参照
            #voltage：出力電圧値。0~+-100
            #Icomp：電流コンプライアンス
            print ('DV '+str(s)+',0,'+str(0)+','+str(icomp))
        for d in D1:
            self.SMU1.write('DV '+str(d)+',0,'+str(0)+','+str(icomp)) #0Vを印加
            print ('DV '+str(d)+',0,'+str(0)+','+str(icomp))
        for b in B1:
            self.SMU1.write('DV '+str(b)+',0,'+str(0)+','+str(icomp)) #0Vを印加
            print ('DV '+str(b)+',0,'+str(0)+','+str(icomp))
        for inv in invalid1:
            self.SMU1.write('DI '+str(inv)+',0,'+str(0)+','+str(vcomp)) #これは？
            #DI：指定されたチャネルから電流を出力
            #DI chnum,irange,current[,Vcomp[,comp_polarity[,vrange]]]
            #chnum：チャネル番号
            #irange：レンジングタイプ。table4.4参照
            #current：出力電流値。0~+-0.1
            #Vcomp：電圧コンプライアンス
            print ('DI '+str(inv)+',0,'+str(0)+','+str(vcomp))

        self.SMU1.write('XE') #測定を開始
        print ('XE') 

        self.SMU1.write('DZ') #指定されたチャネルの設定を記憶して、チャネル出力を0Vに変更
        print ('DZ')

        self.SMU1.write('END') #STで始まったプログラムの終了を意味する
        print ('END')
        print ('**********')

        #SMU２を使わない場合は終了
        if len(S2) == 0 and len(G2) == 0 and len(D2) == 0 and len(invalid2) == 0:
            return
   

    def BIAS_APPLY(self,Vb=dict(zip([i for i in range(1,17)],[0.0 for i in range(1,17)])),
                   Vb_2nd={},Ib={},NP=-1,icomp=1.0e-3,vcomp=20.0,address=101):

        for key in Vb.keys():
            if key in list(Ib.keys()):
                print('WARNING: Both DI and DV commands are required to the one channel.')
        Vb1     = [[k,v] for k,v in Vb.items() if k <9 and k > 0]
        str_Vb1 = str(Vb1).replace('[','').replace(']','')
        Vb1_2nd = [[k,v] for k,v in Vb_2nd.items() if k <9 and k > 0]
        str_Vb1_2nd = str(Vb1_2nd).replace('[','').replace(']','')
        Ib1     = [[k,v] for k,v in Ib.items() if k <9 and k > 0]
        str_Ib1 = str(Ib1).replace('[','').replace(']','')
        Vb2     = [[k-8,v] for k,v in Vb.items() if k >= 9]
        str_Vb2 = str(Vb2).replace('[','').replace(']','')
        Vb2_2nd = [[k-8,v] for k,v in Vb_2nd.items() if k >= 9]
        str_Vb2_2nd = str(Vb2_2nd).replace('[','').replace(']','')
        Ib2     = [[k-8,v] for k,v in Ib.items() if k >= 9]
        str_Ib2 = str(Ib2).replace('[','').replace(']','')
        print('**********')
        self.SMU1.write('ST '+str(address))
        print('ST '+str(address))
        for k,v in Vb1:
            self.SMU1.write('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
            print('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
        for k,v in Vb1_2nd:
            self.SMU1.write('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
            print('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
        for k,v in Ib1:
            self.SMU1.write('DI '+str(k)+',0,'+str(v)+','+str(vcomp))
            print('DI '+str(k)+',0,'+str(v)+','+str(vcomp))
        self.SMU1.write('END')
        print('END')
        print('**********')
        self.SMU2.write('ST '+str(address))
        print('ST '+str(address))
        for k,v in Vb2:
            self.SMU2.write('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
            print('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
        for k,v in Vb2_2nd:
            self.SMU2.write('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
            print('DV '+str(k)+',0,'+str(NP*v)+','+str(icomp))
        for k,v in Ib2:
            self.SMU2.write('DI '+str(k)+',0,'+str(v)+','+str(vcomp))
            print('DI '+str(k)+',0,'+str(v)+','+str(vcomp))
        self.SMU2.write('END')
        print('END')
        print('**********')

    def INV_osci(self,GND=[0],VDD=[2],IN=[1],OUT=[4],Vdd=2.0,icomp=1.0e-3,vcomp=5.0,step=0.1,freq=100):
        # IN: 矩形波入力，OUT: 0A電流源接続として，電位測定
        # step: 測定の時間間隔，freq: 入力信号周波数，duty: 入力矩形波のデューティー比
        # 電圧波形を返す
        GND1 = [g for g in GND if g<9 and g>0]
        GND2 = [g-8 for g in GND if g>=9]
        VDD1 = [v for v in VDD if v<9 and Vdd>0]
        VDD2 = [v-8 for v in VDD if v>=9]
        IN1  = [in_node for in_node in IN if in_node<9 and in_node>0]
        IN2  = [in_node-8 for in_node in IN if in_node>=9]
        OUT1 = [out_node for out_node in OUT if out_node<9 and out_node>0]
        OUT2 = [out_node-8 for out_node in OUT if out_node>=9]
        result = []
        T = float(1)/float(freq)

        # SMU内部メモリに入力波形用プログラムと測定用プログラムを書き込み
        # GND,VDD,VOUT部分
        self.SMU1.write('ST 201')
        for gnd in GND1:
            self.SMU1.write('DV '+str(gnd)+',0,'+str(0)+','+str(icomp))
        for v in VDD1:
            self.SMU1.write('DV '+str(v)+',0,'+str(Vdd)+','+str(icomp))
        for out in OUT1:
            self.SMU1.write('DI '+str(out)+',0,'+str(0)+','+str(vcomp))
        self.SMU1.write('END')
        self.SMU2.write('ST 201')
        for gnd in GND2:
            self.SMU2.write('DV '+str(gnd)+',0,'+str(0)+','+str(icomp))
        for v in VDD2:
            self.SMU2.write('DV '+str(v)+',0,'+str(Vdd)+','+str(icomp))
        for out in OUT2:
            self.SMU2.write('DI '+str(out)+',0,'+str(0)+','+str(vcomp))
        self.SMU2.write('END')

        # 入力信号HIGH -> LOW -> HIGH
        addr_list = []
        A = np.arange(Vdd,0.0,-step)
        B = np.arange(0.0,Vdd,step)
        in_sig = np.concatenate([A,B])
        for Vin,i in zip(in_sig,range(len(in_sig))):
            self.SMU1.write('ST {}'.format(202+i))
            for input_node in IN1:
                self.SMU1.write('DV '+str(input_node)+',0,'+str(Vin)+','+str(icomp))
            self.SMU1.write('END')
            if Vin == Vdd:
                high_addr = 202+i
            elif Vin == 0:
                low_addr  = 202+i
            addr_list.append(202+i)

        for Vin,i in zip(in_sig,range(len(in_sig))):
            self.SMU2.write('ST {}'.format(202+i))
            for input_node in IN2:
                self.SMU2.write('DV '+str(input_node)+',0,'+str(Vin)+','+str(icomp))
            self.SMU2.write('END')

        return addr_list,high_addr,low_addr,in_sig

    def spot_meas(self, ch=range(1,17), mparam=['I' for i in range(1,17)]):
        ch1 = [c for c in ch if c<9 and c>0]
        mp1 = [mparam[i] for i in range(len(mparam)) if i < 8]
        ch2 = [c-8 for c in ch if c>=9]
        mp2 = [mparam[i] for i in range(len(mparam)) if i >= 8]
        # （有効化した）全チャネルの高速スポット測定を実行
        for ch, mp in zip(ch1, mp1):
            if mp == 'I':
                self.SMU1.write('TTI {}, 11'.format(ch))
            elif mp == 'V':
                self.SMU1.write('TTV {}, 0'.format(ch))
            elif mp == 'IV':
                print ('ERROR: The measurement parameter is not given in correct format.')
                print ('Please type ''I'' or ''V''')
                self.SMU1.close()
                self.SMU2.close()
                exit()
            self.SMU1.query('*OPC?')
        for ch, mp in zip(ch2, mp2):
            if mp == 'I':
                self.SMU2.write('TTI {}, 11'.format(ch))
            elif mp == 'V':
                self.SMU2.write('TTV {}, 0'.format(ch))
            elif mp == 'IV':
                print ('ERROR: The measurement parameter is not given in correct format.')
                print ('Please type ''I'' or ''V''')
                self.SMU1.close()
                self.SMU2.close()
                exit()
            self.SMU2.query('*OPC?')

    def read_buff(self,total_meas=31,ch=range(1,17),in_sign=[[0.1 for i in range(31)]]):
        # 測定器のデータ出力バッファを読み出す
        # 1チャネルの測定結果-16Byte
        # チャネル毎に時刻，データの順
        # 第2引数は，1列当たりのデータ数を定める（(時刻+データ)*2=16）
        # TODO: SMU2を測定に用いない場合への対応（これで大丈夫？）
        print ('reading the data...')
        ch1 = [c for c in ch if c<9 and c>0]
        ch2 = [c-8 for c in ch if c>=9]
        if len(ch1) > 0:
            print (self.SMU1.query('ERR?'))
            buff_data1 = self.SMU1.read_bytes((3+12+1)*2*len(ch1)*total_meas) # (3桁+12桁+delimiter) * (時刻，I or V) * 有効チャネル数 * 測定回数
            buff_data1 = buff_data1.decode('utf-8').split(',')
        else:
            buff_data1 = []
        if len(ch2) > 0:
            print (self.SMU2.query('ERR?'))
            #print (ch2,(3+12+1)*2*len(ch2)*total_meas)
            buff_data2 = self.SMU2.read_bytes((3+12+1)*2*len(ch2)*total_meas) # (3桁+12桁+delimiter) * (時刻，I or V) * 有効チャネル数 * 測定回数
            #print (buff_data2)
            buff_data2 = buff_data2.decode('utf-8').split(',')
        else:
            buff_data2 = []
        split_data1,split_data2,spot1,spot2 = [],[],[],[]
        #print (buff_data1,buff_data2)
        for d1,d2,i in zip_longest(buff_data1,buff_data2,range(max(len(buff_data1),len(buff_data2)))):
            spot1.append(d1)
            spot2.append(d2)
            if (len(ch1) > 0) and (i%(len(ch1)*2)==(len(ch1)*2-1)) and (i < len(buff_data1)):
                split_data1.append(spot1)
                spot1 = []
            if (len(ch2) > 0) and (i%(len(ch2)*2)==(len(ch2)*2-1)) and (i < len(buff_data2)):
                split_data2.append(spot2)
                spot2 = []
        mdata_list = []
        #print (split_data1)
        #print (split_data2)
        #print (len(split_data1),len(split_data2),max(len(split_data1),len(split_data2)))
        for ds1,ds2,c in zip_longest(split_data1,split_data2,range(max(len(split_data1),len(split_data2)))):
            if ds1 is None:
                ds1 = []
            if ds2 is None:
                ds2 = []
            #print (type(d1),type(d2))
            mtime,data1,data2 = [],[],[]
            for d1,d2,i in zip_longest(ds1,ds2,range(max(len(ds1),len(ds2)))):
                if i%2==0:
                    if d1 is not None and d1 is not '':
                        d1 = d1[3:]
                        mtime.append(float(d1))
                    if d2 is not None and d2 is not '':
                        d2 = d2[3:]
                        mtime.append(float(d2))
                else:
                    data1.append(d1)
                    data2.append(d2)
            mtime=np.mean(mtime)
            sta1,val1,sta2,val2 = "","","",""
            for d1 in data1:
                if d1 is not None:
                    sta1 += ',' + d1[0:3]
                    val1 += ',' + d1[3:]
                else:
                    sta1 += ''
                    val1 += ''
            for d2 in data2:
                if d2 is not None:
                    sta2 += ',' + d2[0:3]
                    val2 += ',' + d2[3:]
                else:
                    sta2 += ''
                    val2 += ''
            mdata = str(mtime) # セーブデータの先頭（タイムスタンプ）
            for k in in_sign:
                mdata += ','+str(k[c]) # 掃引パラメータ等を追加
            mdata += val1+val2+sta1+sta2+'\n' # 測定データとステータスを追加
            #print (mdata)
            mdata_list.append(mdata)
        if 'self.SMU1' in locals():
            self.SMU1.write('BC') # データ出力バッファクリア
        if 'self.SMU2' in locals():
            self.SMU2.write('BC') # データ出力バッファクリア
        return mdata_list

    def error_check(self):
        err1 = self.SMU1.query('ERR? 1')
        err2 = self.SMU2.query('ERR? 1')
        if int(err1)==0 and int(err2)==0:
            print ('NO ERROR')
        else:
            msg1 = self.SMU1.query('EMG? '+str(err1))
            print (self.idn1)
            print ('SMU1 error: '+str(err1)+'\n'+str(msg1))
            msg2 = self.SMU2.query('EMG? '+str(err2))
            print (self.idn2)
            print ('SMU2 error: '+str(err2)+'\n'+str(msg2))
            self.close()
        return err1,err2

    def close(self):
        try:
            self.SMU1.write('DZ')
            self.SMU1.write('CL')
            self.SMU1.close()
            self.SMU2.write('DZ')
            self.SMU2.write('CL')
            self.SMU2.close()
        except:
            print ('E5270B ERROR')

if __name__=='__main__':
    measure = OSCILLO()
    source = E5270()
    source.setting([5,6],1)
    measure.setting("RIS")
    v = 0
    source.input_V(5,0,0.0001)
    source.input_V(6,0,0.0001)
    for j in range(5):
        v=0
        for i in range(28):
            source.input_V(5,v,0.0001)
            source.input_V(6,(v/2),0.0001)
            v=v+0.1
            time.sleep(0.01)
    measure.logging("E:Measurement/test2")
    source.close()
    measure.close()
