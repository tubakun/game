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

import e5270b

# 測定には16ピンを利用
# 配置
# 0: 無，1: S，2: G，3:D，4: S，5: G，6: D，7: S，8: G，9:D，10: S，11: G，12: D，13: S，14: G，15: D

class MEASURE():
    def __init__(self,date=datetime.now().strftime("%Y%m%d")):
        # 測定結果格納用ディレクトリの作成
        self.nowtime = date
        print (self.nowtime)
        self.dir = 'C:/Users/kanta/Desktop/prom'+str(self.nowtime)
        if not(os.path.isdir(self.dir)):
            os.makedirs(self.dir)
            print ("Make Directory: "+str(self.dir))



    def SMU_setting(self,ch=[i for i in range(1,17)],mparam=['I' for i in range(1,17)],mode='spot'):
        # SMUの初期設定を行う．chはSMU1の，ch2はSMU2の使用するチャネルをそれぞれ指定する．
        self.SMU = e5270b.E5270_twin(GPIB0='GPIB0::9::INSTR',GPIB1='GPIB1::17::INSTR')
        # チャネルの設定
        # mparamは測定モードを指定
        # 'I': 全チャネル電流測定，'V': 全チャネル電圧測定，'IV': 各チャネルのコンプライアンス側測定
        self.SMU.setting(ch=ch,mparam=mparam,mode=mode)



    def TFT_IDVGS(self,ch_list=range(1,4),mparam=['I' for i in range(1,4)],
                  ar_name='p_L50W1000-1',NP=+1,mset=1,Vdd=2.5,Vs=-0.5,Ve=2.5,step=0.1):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
        # 測定データ保存用ディレクトリの作成
        sdir = self.dir+"/"+str(ar_name)
        save_filename = "mset_"+str(mset)+"_IDVGS.csv"
        # SMUの出力ファイルのヘッダ，パスを生成
        SMU_header='time,vs,vg,vd,is,ig,id,sct1,sct2,sct3\n'
        if ((not os.path.isdir(sdir))):
            os.makedirs(sdir)
            print ("Make Directory: "+str(sdir))
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())

        # SMUへのプログラム書き込み
        sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ ←?
        self.SMU.IVmeas_sweep(SGDB_set=[[1,2,3,4]],none_ch=[],NP=NP,Vdd=Vdd,vstart=Vs,vend=Ve,vstep=step)
        print ('programing has been completed.')

        print ('Measurement start.')
        t0 = time.time()
        time_tmp = time.time()
        # スイッチ（SMUへ接続）
        # ID-VGS曲線測定
        self.SMU.SMU1.write('TSR') #タイマーのカウントをリセット
        self.SMU.SMU1.write('DO 1') #プログラムメモリ内のプログラムを指定された順に実行
        self.SMU.SMU1.query("*OPC?") #実行中の動作をモニタする。実行中の動作がなくなったときに１を返す
        self.SMU.SMU1.write('DZ') #指定されたチャネルの設定を記憶して、チャネル出力を0Vに変更する
        # 測定結果を保存
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=len(sweep_param),ch=ch_list,
                                      in_sign=[[0.0 for i in range(len(sweep_param))],
                                               np.array(sweep_param)*NP,
                                               [NP*Vdd for i in range(len(sweep_param))]])
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=(sdir+'/'+save_filename),wa='w')
        print ('Total easurement time: {}'.format(time.time()-t0))


def save(self,SMU_header='',SMU_data=[],SMU_fpath='test',LCR_header='',LCR_fpath='test',wa='w'):
        # SMU測定データ保存
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa=wa)
        # LCRメーター測定データ保存（測定データは内部メモリに格納されている）
        self.LCR_save(LCR_header=LCR_header,LCR_fpath=LCR_fpath)


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
        ar_name = 'ext-ext_L300_W200_Wb100_140' # 1 ~ 140

        #NP = -1 # p型のみ搭載
        #今回はpnによらず正の電圧をかけていくので、NPは１
        NP = 1

        measure.TFT_IDVGS(ar_name=ar_name,NP=NP,mset=1,Vdd=2.5,Vs=-0.5,Ve=2.5,step=0.1)

        #ここから下が分からない
        input()
        for i in [0,1]:
            if i > 0:
                measure.TFT_IDVGS(ar_name=ar_name,NP=NP,mset=(i*2+1),Vdd=2.5,Vs=-0.5,Ve=2.5,step=0.1)
            measure.TFT_IDVGS(ar_name=ar_name,NP=NP,mset=(i*2+2),Vdd=2.5,Vs=2.5,Ve=-0.5,step=-0.1)
        measure.TFT_IDVDS(ar_name=ar_name,NP=NP,mset=5,Vgs_l=[0.0,0.5,1.0,1.5,2.0,2.5],Vs=0.0,Ve=2.5,step=0.1)


    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        measure.close()
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)


#測定チャネルの指定方法
#掃引測定モードに設定する（MM 2 または MM 16）


