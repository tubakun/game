###########################################
# for PUF chip measurement (2202_oshima)  #
###########################################
ICOMP = 0.1   # 電流コンプライアンス
VCOMP = 10.0    # 電圧コンプライアンス
TWAIT = 1.0e-6 # 入力信号安定用待ち時間

from datetime import datetime
import pyvisa as visa
import time, sys, os, re
import numpy as np
from math import exp
import signal

import e5270b2_DS

#たりないかも
#アナコンダで居れたら動く

# 測定には16ピンを利用
# 配置
# 0: 無，1: S，2: G，3:D，4: S，5: G，6: D，7: S，8: G，9:D，10: S，11: G，12: D，13: S，14: G，15: D

class MEASURE():
    def __init__(self,date=datetime.now().strftime("%Y%m%d")):
        # 測定結果格納用ディレクトリの作成
        self.nowtime = date
        print (self.nowtime)
        self.dir = 'c:/Users/kanta/Desktop/prom/'+str(self.nowtime)
        if not(os.path.isdir(self.dir)):
            os.makedirs(self.dir)
            print ("Make Directory: "+str(self.dir))

    def SMU_setting(self,ch=[i for i in range(1,5)],mparam=['I' for i in range(1,5)],mode='spot'):#関数の値はデフォルト値、指定がない場合これになる
        # SMUの初期設定を行う．chはSMU1の，ch2はSMU2の使用するチャネルをそれぞれ指定する．
        self.SMU = e5270b2_DS.E5270_twin(GPIB0='GPIB0::9::INSTR',GPIB1='GPIB2::17::INSTR')
        # チャネルの設定
        # mparamは測定モードを指定
        # 'I': 全チャネル電流測定，'V': 全チャネル電圧測定，'IV': 各チャネルのコンプライアンス側測定
        self.SMU.setting(ch=ch,mparam=mparam,mode=mode)


    def TFT_IDVGS(self,ch_list=range(1,5),mparam=['I' for i in range(1,5)],
                  ar_name='p_L50W1000-1',NP=+1,mset=1,V=2.5,icomp=1.0e-5,Vg=0,per=600):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='spot')
        # 測定データ保存用ディレクトリの作成
        sdir = self.dir+"/"+str(ar_name)
        save_filename = "mset_"+str(mset)+"_IDVGS.csv"
        # SMUの出力ファイルのヘッダ，パスを生成
        SMU_header='time,vd,vs,vg,vb,id,is,ig,ib,sct1,sct2,sct3,sect4\n'
        if ((not os.path.isdir(sdir))):
            os.makedirs(sdir)
            print ("Make Directory: "+str(sdir))
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())
        # SMUへのプログラム書き込み
        #一つの電圧値ごとの測定回数
        sweep_param_list = [value for value in [(V + (0.1 * i))*NP for i in range(0, 10)] for _ in range(per)] # 掃引パラメータ
        num = len(sweep_param_list)
        pram = [value for value in [(V + (0.1 * i))*NP for i in range(0, 10)] for _ in range(1)]
        #SGDB順番注意
        #self.SMU.IVmeas_sweep(SGDB_set=[[1,2,3,4]],none_ch=[],NP=NP,Vdd=Vdd,vstart=3.0,vend=3.0,vstep=step)
        #self.SMU.IVmeas_sweep(SGDB_set=[[2,3,1,4]],none_ch=[],NP=1,Vdd=0,vstart=vstart,vend=vend,vstep=0.1,icomp=1.0e-3,vcomp=15, tot_step=tot_step)
        self.SMU.IVmeas_spot(SGDB_set=[[2,3,1,4]],none_ch=[],NP=1,sweep_param=pram,icomp=icomp,vcomp=15,Vg=Vg)
        print ('programing has been completed.')
        print ('Measurement start.')
        t0 = time.time()
        time_tmp = time.time()
        # スイッチ（SMUへ接続）
        # ID-VGS曲線測定
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU1.write('DO 1')
        self.SMU.SMU1.query("*OPC?")

        #プログラムの動作をNMOSで確認

        #破壊用
        time.sleep(1)
        for k in range(len(pram)):
            self.SMU.SMU1.write('DO '+str(k+2))
            print ('Now measuring.')
            for i in range(per): 
                self.SMU.SMU1.query('*OPC?')
                self.SMU.SMU1.write('XE')
                self.SMU.SMU1.query('*OPC?')
                time.sleep(0.09)


                       
        self.SMU.SMU1.write('DZ')
        # 測定結果を保存
        # sweep_paramの数が保存するデータの数になっているので、階段波掃引測定するときはtot_stepの数にしないといけない
        SMU_data = []
        
        SMU_data = self.SMU.read_buff(total_meas=num,ch=ch_list,
                                      in_sign=[ np.array(sweep_param_list)*NP,
                                               [0.0 for i in range(num)],
                                                [Vg for i in range(num)],
                                               [0.0 for i in range(num)]])
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=(sdir+'/'+save_filename),wa='w')
        
        #破壊用

        #階段用
        
        # SMU_data = self.SMU.read_buff(total_meas=tot_step,ch=ch_list,
        #                               in_sign=[[0.0 for i in range(tot_step)],
        #                                        [vstart for i in range(tot_step)],
        #                                        [0.0 for i in range(tot_step)],
        #                                        [0.0 for i in range(tot_step)]])
        # self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=(sdir+'/'+save_filename),wa='w')

        print ('Total easurement time: {}'.format(time.time()-t0))

    def SMU_save(self,SMU_header='',SMU_data=[],SMU_fpath='test',wa='w'):
        # SMU測定データ保存
        s_file=open(SMU_fpath,wa)
        s_file.write(SMU_header,)
        for i in range(len(SMU_data)):
            s_file.write(str(SMU_data[i]),)
        s_file.close()

    def close(self):
        try:
            self.SMU.SMU1.write("DZ")
            self.SMU.SMU2.write("DZ")
            self.SMU.SMU1.close()
            self.SMU.SMU2.close()
            #self.e4980.close()
        except:
            print ('E5270B ERROR')


if __name__ == '__main__':
    ##############################################################
    # ゲートタイプ，ゲート幅，アレイ番号，ストレス電圧，要確認!! #
    ##############################################################
    measure = MEASURE()
    try:
        # TFT測定（IV曲線とCGS-VGS曲線を1回測定）
#        ar_name = 'ext-enc_L050_W600_150' # 1 ~ 150
#        ar_name = 'ext-ext_L100_W200_Wb100_140' # 1 ~ 140
#        ar_name = 'ext-ext_L200_W200_Wb100_140' # 1 ~ 140
        #ar_name = 'ext-ext_L300_W200_Wb100_140' # 1 ~ 140
        ar_name = '3_3p_g0'
        V = 1
        mset = -2
        NP = -1
        Vg = 0
        per=6
        icomp = 1.0e-2
        measure.TFT_IDVGS(ar_name=ar_name,NP=NP,mset=mset,V=V,icomp=icomp,Vg=Vg,per=per)

    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        measure.close()
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

#Todo：プログラム改良する
#Todo：分かりやすく


