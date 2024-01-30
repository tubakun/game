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
        self.dir = 'c:/Users/oshima/work/measurement_data/2301_oshima/chip_20230614_2/'+str(self.nowtime)
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
        sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ
        self.SMU.IVmeas_sweep(SGD_set=[[1,2,3]],none_ch=[],NP=NP,Vdd=Vdd,vstart=Vs,vend=Ve,vstep=step)
        print ('programing has been completed.')
        print ('Measurement start.')
        t0 = time.time()
        time_tmp = time.time()
        # スイッチ（SMUへ接続）
        # ID-VGS曲線測定
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU1.write('DO 1')
        self.SMU.SMU1.query("*OPC?")
        self.SMU.SMU1.write('DZ')
        # 測定結果を保存
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=len(sweep_param),ch=ch_list,
                                      in_sign=[[0.0 for i in range(len(sweep_param))],
                                               np.array(sweep_param)*NP,
                                               [NP*Vdd for i in range(len(sweep_param))]])
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=(sdir+'/'+save_filename),wa='w')
        print ('Total easurement time: {}'.format(time.time()-t0))

    def TFT_IDVDS(self,ch_list=range(1,4),mparam=['I' for i in range(1,4)],
                  ar_name='p_L50W1000-1',NP=+1,mset=1,Vgs_l=[0.5*i for i in range(6)],Vs=0.0,Ve=2.5,step=0.1):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
        # 測定データ保存用ディレクトリの作成
        sdir = self.dir+"/"+str(ar_name)
        # SMUの出力ファイルのヘッダ，パスを生成
        SMU_header='time,vs,vg,vd,is_1,ig_1,id_1,\n'
        if ((not os.path.isdir(sdir))):
            os.makedirs(sdir)
            print ("Make Directory: "+str(sdir))
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(close())
        t0 = time.time()
        for i,Vgs in enumerate(Vgs_l):
            print(i,Vgs)
            # SMUへのプログラム書き込み
            save_filename = "mset_"+str(mset+i)+"_IDVDS.csv"
            sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ
            self.SMU.IVmeas_sweep(SGD_set=[[1,3,2]],none_ch=[],NP=NP,Vdd=Vgs,vstart=Vs,vend=Ve,vstep=step)
            print ('programing has been completed.')
            print ('Measurement start.')
            time_tmp = time.time()
            # ID-VGS曲線測定
            self.SMU.SMU1.write('TSR')
            self.SMU.SMU1.write('DO 1')
            self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU1.write('DZ')
            # 測定結果を保存
            SMU_data = []
            SMU_data = self.SMU.read_buff(total_meas=len(sweep_param),ch=ch_list,
                                          in_sign=[[0.0 for i in range(len(sweep_param))],
                                                   [NP*Vgs for i in range(len(sweep_param))],
                                                   np.array(sweep_param)*NP])
            self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=os.path.join(sdir,save_filename),wa='w')
        print ('Total easurement time: {}'.format(time.time()-t0))

    def TFT_cap(self,conn_sgd=[],ar_name='p_L50W1000-1',sparam='Vbias',VS=0.0,Vbias=0.0,mset=1):
        # 補正データの呼び出し用クラス
        #self.correction = correction.CORRECTION()
        # 測定機器の初期設定
        if sparam == 'Vbias':
            func, freq, table, VAC = 'CPRP', 3000.0, [-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0.0,0.5], 0.1
        elif sparam == 'VS':
            func, freq, table, VAC = 'CPRP', 3000.0, [-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0.0,0.5], 0.1
        #func, freq, Vbias, VS, sparam, table, VAC = 'CPRP', 3000.0, 0.0, 0.0, 'Vbias', [0.0,NP*0.5,NP*1.0,NP*1.5,NP*2.0,NP*2.5], 0.1
        #func, freq, Vbias, VS, sparam, table, VAC = 'ZTR', 1000.0, 2.5, 0.0, 'freq', [20.0*exp(float(2.5*i) * 0.0575646273249) for i in range(81)], 0.1
        self.LCR_setting(func=func,freq=freq,Vbias=Vbias,VS=VS,VAC=VAC)
        self.SW = e5252a.E5252A(name='GPIB2::22::INSTR')
        # 測定データ保存用ディレクトリzの作成
        loop_dir  = self.dir+'/{0}'.format(ar_name)
        cap_dir   = loop_dir+'/cap'
        # LCRメータの出力ファイルのヘッダ，パスを生成
        LCR_header = measure.LCR_headergen(func=func,sparam=sparam)
        if (not os.path.isdir(cap_dir)):
            os.makedirs(cap_dir)
            print ("Make Directory: "+str(cap_dir))
        if (os.path.isfile(cap_dir+'/dev_0_mset_{0}.csv'.format(mset))):
            print ('The measurement result files already exist.')
            sys.exit()
        # SWの切替前に一度LCRメータの出力を止める
        self.LCR.stop_output()
        t0 = time.time()
        # 容量測定
        for conn_s, conn_g, conn_d, dev_num in zip(conn_sgd[0],conn_sgd[1],conn_sgd[2],range(len(conn_sgd[0]))):
            LCR_fpath  = cap_dir+'/dev_{0}_mset_{1}.csv'.format(dev_num,mset)
            time_tmp = time.time()
            #self.correction.read_corr_data(dev_num)
            # スイッチ（SMUへ接続）
            self.SW.normal_setting(conn=[conn_s,conn_g,conn_d])
            self.LCR.sweep(sparam=sparam,table=table,VAC=VAC)
            print ('LCRmeter measurement time for dev. #{0}: {1}'.format(dev_num, time.time()-time_tmp))
            self.LCR.stop_output()
            # 測定結果を保存
            self.LCR_save(LCR_header=LCR_header, LCR_fpath=LCR_fpath, wa='w')
        print ('total measurement time: {}'.format(time.time()-t0))

    def cap_IV(self,ch_list=range(1,3),mparam=['I' for i in range(1,3)],
               conn_sgd=[],vstress=1000,istress=1000,stress_time=0.1,
               ar_name='cap_array-1',mset=1,Vdd=0.0,Vs=-2.5,Ve=2.5,step=0.1):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
        self.SW = e5252a.E5252A(name='GPIB2::22::INSTR')
        # 測定データ保存用ディレクトリの作成
        loop_dir  =self.dir+'/'+str(ar_name)
        IV_dir = loop_dir+'/IV'
        SMU_header='time,V,Ial_0,Iau_0,\n'

        if ((not os.path.isdir(IV_dir))):
            os.makedirs(IV_dir)
            print ("Make Directory: "+str(IV_dir))
        if ((os.path.isfile(IV_dir+'/dev_num_0_set_{0}.csv'.format(mset)))):
            print ('The measurement result files already exist.')
            sys.exit()
        # SMUへのプログラム書き込み
        sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ
        self.SMU.IVmeas_sweep(SGD_set=[[1,2,'nan']],none_ch=[],NP=+1,Vdd=Vdd,vstart=Vs,vend=Ve,vstep=step)
        if vstress != 1000 and istress == 1000:
            self.SMU.BIAS_APPLY(Vb={1:vstress,2:0.0},NP=+1)
        elif vstress == 1000 and istress != 1000:
            print("Istress is applied.")
            self.SMU.BIAS_APPLY(Ib={1:istress,2:istress*(-1.0)},NP=+1)
        elif vstress != 1000 and istress != 1000:
            print('ERROR: Both Istress and Vstress are required.')
            sys.exit()
        print ('programing has been completed.')
        print ('Measurement start.')
        t0 = time.time()
        # 測定開始
        for conn_s, conn_g, conn_d, dev_num in zip(conn_sgd[0],conn_sgd[1],conn_sgd[2],range(len(conn_sgd[0]))):
            SMU_fpath  = IV_dir+'/dev_num_{0}_set_{1}.csv'.format(dev_num,mset)
            # スイッチ（SMUへ接続）
            self.SW.normal_setting(conn=[conn_s,conn_g,conn_d])
            if vstress != 1000 or istress != 1000:
                self.SMU.SMU1.write('DO 101')
                stress_start = time.time()
                self.SMU.SMU1.query("*OPC?")
                print('DO 101')
                while((time.time()-stress_start)<stress_time):
                    time.sleep(stress_time*0.01)
            self.SMU.SMU1.write('TSR')
            self.SMU.SMU1.write('DO 1')
            self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU1.write('DZ')
            # 測定結果を保存
            SMU_data = []
            SMU_data = self.SMU.read_buff(total_meas=len(sweep_param),ch=ch_list,
                                          in_sign=[np.array(sweep_param),[Vdd for i in range(len(sweep_param))]])
            self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        print ('Total measurement time: {}'.format(time.time()-t0))

    def cap_VI(self,ch_list=range(1,3),mparam=['V' for i in range(1,3)],
               conn_sgd=[],Ibias_list=[0.1e-9],
               ar_name='cap_array-1',mset=1,Vdd=0.0,Vs=-2.5,Ve=2.5,step=0.1):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='spot')
        self.SW = e5252a.E5252A(name='GPIB2::22::INSTR')
        # 測定データ保存用ディレクトリの作成
        loop_dir  =self.dir+'/'+str(ar_name)
        IV_dir = loop_dir+'/IV'
        SMU_header='time,V,Val_0,Vau_0,\n'

        if ((not os.path.isdir(IV_dir))):
            os.makedirs(IV_dir)
            print ("Make Directory: "+str(IV_dir))
        if ((os.path.isfile(IV_dir+'/dev_num_0_set_{0}.csv'.format(mset)))):
            print ('The measurement result files already exist.')
            sys.exit()
        # SMUへのプログラム書き込み
        sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ
        for Ibias,addr in zip(Ibias_list, range(101,101+len(Ibias_list))):
            self.SMU.BIAS_APPLY(Vb={},Ib={1:Ibias,2:Ibias*(-1.0)},NP=+1,address=addr)
        print ('programing has been completed.')
        print ('Measurement start.')
        t0 = time.time()
        # 測定開始
        for conn_s, conn_g, conn_d, dev_num in zip(conn_sgd[0],conn_sgd[1],conn_sgd[2],range(len(conn_sgd[0]))):
            SMU_fpath  = IV_dir+'/dev_num_{0}_set_{1}.csv'.format(dev_num,mset)
            # スイッチ（SMUへ接続）
            self.SW.normal_setting(conn=[conn_s,conn_g,conn_d])
            self.SMU.SMU1.write('TSR')
            for addr in range(101,101+len(Ibias_list)):
                self.SMU.SMU1.write('DO '+str(addr))
                self.SMU.SMU1.query("*OPC?")
                self.SMU.SMU1.write('XE')
                self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU1.write('DZ')
            # 測定結果を保存
            SMU_data = []
            SMU_data = self.SMU.read_buff(total_meas=len(Ibias_list),ch=ch_list,
                                          in_sign=[np.array(Ibias_list)])
            self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        print ('Total measurement time: {}'.format(time.time()-t0))

    def cap_cap(self,conn_sgd=[],func='ZTR',freq=1000,Vbias=0.0,VS=0.0,sparam='freq',
                table=[20.0*exp(float(2.5*i) * 0.0575646273249) for i in range(81)],VAC=0.1,sdir='cap_1-1',mset=1):
        self.LCR_setting(func=func,freq=freq,Vbias=Vbias,VS=VS,VAC=VAC)
        if not os.path.isdir('{0}/{1}'.format(self.dir,sdir)):
            os.makedirs('{0}/{1}'.format(self.dir,sdir))
            print ("Make Directory: "+'{0}/{1}'.format(self.dir,sdir))
        if os.path.isfile('{0}/{1}/mset_{2}.csv'.format(self.dir,sdir,mset)):
            print ("The measurement result file already exists. Exit the program...")
            sys.exit()

        LCR_header = measure.LCR_headergen(func=func,sparam=sparam)
        t0         = time.time()
        fname      = self.dir+'/'+sdir+'/'+'mset_'+str(mset)+'.csv'
        time_tmp   = time.time()
        self.LCR.sweep(sparam=sparam,table=table,VAC=VAC)
        print ('LCRmeter measurement time: {0}'.format(time.time()-time_tmp))
        self.LCR.stop_output()
        # 測定結果を保存
        self.LCR_save(LCR_header=LCR_header, LCR_fpath=fname, wa='w')
        print ('total measurement time: {}'.format(time.time()-t0))

    def romcell(self,ch_list=range(1,6),array_name='romcell-1',mset=1,
                Vsl_wr=5.0,Vsl_rd=0.0,read_time=20,write_time=1,mode='r'):
        '''
        ROMセル測定用関数．Vslを変えることで書き込み/読み出しを切り替える
        1pin x 5を利用
        '''
        sdir = self.dir + '/' + array_name
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
            print("Make directory: "+str(sdir))
        Vsl = Vsl_wr * (mode=="w") + Vsl_rd * (mode=="r")
        Vwl = Vsl-2.5
        meas_time = write_time * (mode=="w") + read_time * (mode=="r")
        if mode == 'r':
            save_filename = "mset_"+str(mset)+"_read_Vsl"+str(Vsl)+".csv"
        if mode == 'w':
            save_filename = "mset_"+str(mset)+"_write_Vsl"+str(Vsl)+".csv"
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())
        # SMUの出力ファイルのヘッダ，パスを生成
        node_dict={'wl':[ch_list[0]],'sl':[ch_list[1]],'gl':[ch_list[2]],
                   'bl':[ch_list[4]],'mn':[ch_list[3]]}
        mparam=['I','I','I','V','V']

        Ib = {ch_list[3]: 0.0, ch_list[4]: 0.0}
        Vb = {ch_list[0]: Vwl, ch_list[1]: Vsl, ch_list[2]: 0.0}
        SMU_header='time,vwl,vsl,vgl,imn,ibl,iwl,isl,igl,vmn,vbl,sct1,sct2,sct3,sct4,sct5,\n'


        #node_dict={'wl':[8],'sl':[9],'gl':[10],'bl':[11],'mn':[12]}
        #
        #mparam=['V','V','I','V','V','V','V',
        #        'I','I','I','V','V']
        #Ib = {4:0.0, 5:0.0, 3:0.0, 4:0.0,
        #      5:0.0, 6:0.0, 7:0.0, 8:0.0, 12:0.0, 13:0.0}
        #Vb = {1:0.0, 2: Vsl, 3:0.0}
        #SMU_header=('time,Vwl1,Vsl1,Vgl1,Imn1,Ibl1,'+
        #            'Idd_sram,Iwl_sram,Iss_sram,'+
        #            'Iwl2,Isl2,Igl2,Imn2,Ibl2,'+
        #            'Iwl1,Isl1,Igl1,Vmn1,Vbl1,'+
        #            'Vdd_sram,Vwl_sram,Vss_sram,'+
        #            'Vwl2,Vsl2,Vgl2,Vmn2,Vbl2\n')
        #
        #mparam=['V','V','V','V',
        #        'V','V','V','V',
        #        'I','I','I','V','V']
        #Ib = {1:0.0, 2:0.0, 3:0.0, 4:0.0,
        #      5:0.0, 6:0.0, 8:0.0, 7:0.0, 12:0.0, 13:0.0}
        #Vb = {9:0.0, 10:Vsl, 11:0.0}
        #SMU_header=('time,Iwl1,Isl1,Igl1,Imn1,Ibl1,'+
        #            'Idd_sram,Iwl_sram,Iss_sram,'+
        #            'Vwl2,Vsl2,Vgl2,Imn2,Ibl2,'+
        #            'Vwl1,Vsl1,Vgl1,Vmn1,Vbl1,'+
        #            'Vdd_sram,Vwl_sram,Vss_sram,'+
        #            'Iwl2,Isl2,Igl2,Vmn2,Vbl2\n')

        # SMUへのプログラム書き込み
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='spot')
        self.SMU.BIAS_APPLY(Vb=Vb,Ib=Ib,NP=+1)
        print ('programing has been completed.')
        print ('Measurement start.')
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU2.write('TSR')
        self.SMU.SMU1.write('DO 101')
        self.SMU.SMU2.write('DO 101')
        mstart_time = time.time()
        mcount = 0
        while ((time.time()-mstart_time)<meas_time): # 定めた時間連続測定
            self.SMU.SMU1.write('XE')
            self.SMU.SMU2.write('XE')
            self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU2.query("*OPC?")
            time.sleep(meas_time/1000)
            #time.sleep(0.2)
            mcount += 1
        in_sign = []
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I
        #in_sign.append([0.0 for i in range(mcount)]) # I

        in_sign.append([Vwl for i in range(mcount)]) # Vwl
        in_sign.append([Vsl for i in range(mcount)]) # Vsl
        in_sign.append([0.0 for i in range(mcount)]) # Vgl
        in_sign.append([0.0 for i in range(mcount)]) # Imn
        in_sign.append([0.0 for i in range(mcount)]) # Ibl
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=mcount,ch=ch_list,in_sign=in_sign)
        # 測定（mid nodeの電位確認）結果を保存
        SMU_fpath = sdir + '/' + save_filename
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        self.SMU.SMU1.write('DZ')
        self.SMU.SMU2.write('DZ')
        self.SMU.close()

    def rom_IV(self,ch_list=range(1,3),mparam=['I' for i in range(1,3)],
                  ar_name='rom_1-1',NP=+1,mset=1,Vs=-2.5,Ve=2.5,step=0.1):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
        # 測定データ保存用ディレクトリの作成
        sdir = self.dir+"/"+str(ar_name)
        save_filename = "mset_"+str(mset)+"_IV.csv"
        # SMUの出力ファイルのヘッダ，パスを生成
        SMU_header='time,v1,v2,i1,i2,sct1,sct2,\n'
        if ((not os.path.isdir(sdir))):
            os.makedirs(sdir)
            print ("Make Directory: "+str(sdir))
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(close())
        # SMUへのプログラム書き込み
        sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ
        self.SMU.IVmeas_sweep(SGD_set=[[2,1,'nan']],none_ch=[],
                              NP=NP,Vdd=0.0,vstart=Vs,vend=Ve,vstep=step)
        print ('programing has been completed.')
        print ('Measurement start.')
        t0 = time.time()
        time_tmp = time.time()
        # スイッチ（SMUへ接続）
        # ID-VGS曲線測定
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU1.write('DO 1')
        self.SMU.SMU1.query("*OPC?")
        self.SMU.SMU1.write('DZ')
        # 測定結果を保存
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=len(sweep_param),ch=ch_list,
                                      in_sign=[np.array(sweep_param)*NP,
                                               [0.0 for i in range(len(sweep_param))]])
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=(sdir+'/'+save_filename),wa='w')
        print ('Total easurement time: {}'.format(time.time()-t0))

    def rom_IV_MMmode(self,ch_list=range(1,6),mparam=['I' for i in range(1,6)],
                      ar_name='rom_1-1',NP=+1,mset=1,Vs=-2.5,Ve=2.5,step=0.1):
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
        # 測定データ保存用ディレクトリの作成
        sdir = self.dir+"/"+str(ar_name)
        save_filename = "mset_"+str(mset)+"_IV.csv"
        # SMUの出力ファイルのヘッダ，パスを生成
        SMU_header='time,vAl,vAu,i1,i2,i3,i4,i5,sct1,sct2,sct3,sct4,sct5,\n'
        if ((not os.path.isdir(sdir))):
            os.makedirs(sdir)
            print ("Make Directory: "+str(sdir))
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(close())
        # SMUへのプログラム書き込み
        sweep_param = np.arange(Vs,Ve+step,step,dtype=float) # 掃引パラメータ
        self.SMU.IVmeas_sweep(SGD_set=[[1,2,'nan'],['nan',3,'nan'],['nan',4,'nan'],['nan',5,'nan']],none_ch=[],
                              NP=NP,Vdd=0.0,vstart=Vs,vend=Ve,vstep=step)
        print ('programing has been completed.')
        print ('Measurement start.')
        t0 = time.time()
        time_tmp = time.time()
        # スイッチ（SMUへ接続）
        # ID-VGS曲線測定
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU1.write('DO 1')
        self.SMU.SMU1.query("*OPC?")
        self.SMU.SMU1.write('DZ')
        # 測定結果を保存
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=len(sweep_param),ch=ch_list,
                                      in_sign=[[0.0 for i in range(len(sweep_param))],
                                               np.array(sweep_param)*NP])
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=(sdir+'/'+save_filename),wa='w')
        print ('Total easurement time: {}'.format(time.time()-t0))

    def rom_MMmode(self,ch_list=range(1,6),array_name='rom_1-1',mset=1,
                   V1=5.0,V2=0.0,meas_time=20):
        '''
        ROM測定用関数．Vslを変えることで書き込み/読み出しを切り替える
        1pin x 5を利用
        '''
        sdir = self.dir + '/' + array_name
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
            print("Make directory: "+str(sdir))
        save_filename = "mset_"+str(mset)+"_"+str(V1-V2)+"V.csv"
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())
        # SMUの出力ファイルのヘッダ，パスを生成
        mparam=['I' for i in range(len(ch_list))]

        Vb = {1: V2, 2: V1, 3: V1, 4: V1, 5: V1}
        SMU_header='time,vAl,vAu,i1,i2,i3,i4,i5,sct1,sct2,sct3,sct4,sct5,\n'

        # SMUへのプログラム書き込み
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='spot')
        self.SMU.BIAS_APPLY(Vb=Vb,NP=+1)
        print ('programing has been completed.')
        print ('Measurement start.')
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU2.write('TSR')
        self.SMU.SMU1.write('DO 101')
        self.SMU.SMU2.write('DO 101')
        mstart_time = time.time()
        mcount = 0
        while ((time.time()-mstart_time)<meas_time): # 定めた時間連続測定
            self.SMU.SMU1.write('XE')
            self.SMU.SMU2.write('XE')
            self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU2.query("*OPC?")
            time.sleep(0.1)
            mcount += 1
        in_sign = []

        in_sign.append([V2 for i in range(mcount)]) # Vwl
        in_sign.append([V1 for i in range(mcount)]) # Vsl
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=mcount,ch=ch_list,in_sign=in_sign)
        # 測定（mid nodeの電位確認）結果を保存
        SMU_fpath = sdir + '/' + save_filename
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        self.SMU.SMU1.write('DZ')
        self.SMU.SMU2.write('DZ')
        self.SMU.close()

    def rom(self,ch_list=range(1,3),array_name='rom_1-1',mset=1,
                V1=5.0,V2=0.0,meas_time=20):
        '''
        ROM測定用関数．Vslを変えることで書き込み/読み出しを切り替える
        1pin x 5を利用
        '''
        sdir = self.dir + '/' + array_name
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
            print("Make directory: "+str(sdir))
        save_filename = "mset_"+str(mset)+"_"+str(V1-V2)+"V.csv"
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())
        # SMUの出力ファイルのヘッダ，パスを生成
        mparam=['I','I']

        Vb = {1: V1, 2: V2}
        SMU_header='time,v1,v2,i1,i2,sct1,sct2,\n'

        # SMUへのプログラム書き込み
        self.SMU_setting(ch=ch_list,mparam=mparam,mode='spot')
        self.SMU.BIAS_APPLY(Vb=Vb,NP=+1)
        print ('programing has been completed.')
        print ('Measurement start.')
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU2.write('TSR')
        self.SMU.SMU1.write('DO 101')
        self.SMU.SMU2.write('DO 101')
        mstart_time = time.time()
        mcount = 0
        while ((time.time()-mstart_time)<meas_time): # 定めた時間連続測定
            self.SMU.SMU1.write('XE')
            self.SMU.SMU2.write('XE')
            self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU2.query("*OPC?")
            time.sleep(0.1)
            mcount += 1
        in_sign = []

        in_sign.append([V1 for i in range(mcount)]) # Vwl
        in_sign.append([V2 for i in range(mcount)]) # Vsl
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=mcount,ch=ch_list,in_sign=in_sign)
        # 測定（mid nodeの電位確認）結果を保存
        SMU_fpath = sdir + '/' + save_filename
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        self.SMU.SMU1.write('DZ')
        self.SMU.SMU2.write('DZ')
        self.SMU.close()

    def sram(self,ch_list=range(1,6),array_name="sram-1",mset=1,Vdd=2.5,read_time=10):
        '''
        SRAMセルの読み出し用関数．Vddを変えることで書き込み中や通常動作時の値を読み出せる．
        1pin x 5を利用．
        '''
        sdir = self.dir + '/' + array_name
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
            print("Make directories: "+str(sdir))
        save_filename = "mset_"+str(mset)+"_read_Vdd"+str(Vdd)+".csv"
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())
        Ib = {1: 0.0, 4: 0.0}
        Vb = {2: Vdd, 3: 0.0, 5: 0.0}
        mparam=['V','I','I','V','I']
        node_dict={'bl':[1],'dd':[2],'wl':[3],'blbar':[4],'ss_sram':[5]}
        SMU_header='time,Ibl,Vdd,Vwl,Iblbar,VGND,Vbl,Idd,Iwl,Vblbar,IGND,sct1,sct2,sct3,sct4,sct5,\n'

        self.SMU_setting(ch=ch_list,mparam=mparam,mode='spot')
        self.SMU.BIAS_APPLY(Vb=Vb,Ib=Ib,NP=+1)
        print ('programing has been completed.')
        print ('Measurement start.')
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU2.write('TSR')
        self.SMU.SMU1.write('DO 101')
        self.SMU.SMU2.write('DO 101')
        mstart_time = time.time()

        mcount = 0
        while ((time.time()-mstart_time)<read_time): # 定めた時間連続測定
            self.SMU.SMU1.write('XE')
            self.SMU.SMU2.write('XE')
            self.SMU.SMU1.query("*OPC?")
            self.SMU.SMU2.query("*OPC?")
            mcount += 1
        # 測定（mid nodeの電位確認）結果を保存
        in_sign = []
        for ch in ch_list:
            for val in node_dict.values():
                for node in val:
                    if node == ch and node in Vb:
                        in_sign.append([Vb[node] for i in range(mcount)])
                    elif node == ch and node in Ib:
                        in_sign.append([Ib[node] for i in range(mcount)])
                    else:
                        continue
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=mcount,ch=ch_list,in_sign=in_sign)
        SMU_fpath  = sdir+"/"+save_filename
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        self.SMU.SMU1.write('DZ')
        self.SMU.SMU2.write('DZ')
        self.SMU.close()


    def sram_butterfly(self,ch_list=range(1,6),array_name="sram-1",mset=1,Vdd=2.5,vstart=0.0,vend=2.5,vstep=0.1,bflag=False):
        '''
        SRAMセルの読み出し用関数．Vddを変えることで書き込み中や通常動作時の値を読み出せる．
        1pin x 5を利用．
        '''
        sdir = self.dir + '/' + array_name
        if not os.path.isdir(sdir):
            os.makedirs(sdir)
            print("Make directories: "+str(sdir))
        for fname in os.listdir(sdir):
            if "mset_"+str(mset) in fname:
                print ('The same mset number file is detected. Exit program.')
                sys.exit(self.close())
        if bflag:
            Ib = {1: 0.0}
            Vb = {2: Vdd, 3: 0.0, 5: 0.0}
            Vsweep = [4]
            mparam=['V','I','I','I','I']
            self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
            node_dict={'bl':[1],'dd':[2],'wl':[3],'blbar':[4],'ss_sram':[5]}
            SMU_header='time,Ibl,Vdd,Vwl,Vblbar,VGND,Vbl,Idd,Iwl,Iblbar,IGND,sct1,sct2,sct3,sct4,sct5,\n'
            self.SMU.IVmeas_sweep(SGD_set=[[5,4,2],[3,'nan','nan']],
                                none_ch=[1],NP=+1,Vdd=Vdd,
                                vstart=vstart,vend=vend,vstep=vstep)
            save_filename = ("mset_"+str(mset)+"_bfcurveb_"+
                            str(vstart).replace(".","")+"-"+
                            str(vend).replace(".","")+".csv")
        else:
            Ib = {4: 0.0}
            Vb = {2: Vdd, 3: 0.0, 5: 0.0}
            Vsweep = [1]
            mparam=['I','I','I','V','I']
            self.SMU_setting(ch=ch_list,mparam=mparam,mode='sweep')
            node_dict={'bl':[1],'dd':[2],'wl':[3],'blbar':[4],'ss_sram':[5]}
            SMU_header='time,Vbl,Vdd,Vwl,Iblbar,VGND,Ibl,Idd,Iwl,Vblbar,IGND,sct1,sct2,sct3,sct4,sct5,\n'
            self.SMU.IVmeas_sweep(SGD_set=[[5,1,2],[3,'nan','nan']],
                                none_ch=[4],NP=+1,Vdd=Vdd,
                                vstart=vstart,vend=vend,vstep=vstep)
            save_filename = ("mset_"+str(mset)+"_bfcurve_"+
                            str(vstart).replace(".","")+"-"+
                            str(vend).replace(".","")+".csv")
        print ('programing has been completed.')
        print ('Measurement start.')
        self.SMU.SMU1.write('TSR')
        self.SMU.SMU1.query("*OPC?")
        self.SMU.SMU1.write('DO 1')
        self.SMU.SMU1.query("*OPC?")
        self.SMU.SMU1.write('DZ')
        # 測定（mid nodeの電位確認）結果を保存
        in_sign = []
        vs_list  = np.arange(vstart,(vend+vstep),vstep)
        for ch in ch_list:
            for val in node_dict.values():
                for node in val:
                    if node == ch and node in Vb:
                        in_sign.append([Vb[node] for i in range(len(vs_list))])
                    elif node == ch and node in Ib:
                        in_sign.append([Ib[node] for i in range(len(vs_list))])
                    elif node==ch and node  in Vsweep:
                        in_sign.append([ele for ele in vs_list])
        print(in_sign)
        SMU_data = []
        SMU_data = self.SMU.read_buff(total_meas=len(vs_list),ch=ch_list,in_sign=in_sign)
        SMU_fpath  = sdir+"/"+save_filename
        self.SMU_save(SMU_header=SMU_header,SMU_data=SMU_data,SMU_fpath=SMU_fpath,wa='w')
        self.SMU.SMU1.write('DZ')
        self.SMU.SMU2.write('DZ')
        self.SMU.close()


    def LCR_headergen(self,func='CPD',sparam='freq'):
        if re.match('C..',func):
            main = 'C [F]'
            if re.match('..D',func):
                sub = 'Loss fact.'
            elif re.match('..Q',func):
                sub = 'Qual. fact.'
            elif re.match('..R',func):
                sub = 'R [Ohm]'
        elif re.match('Z..',func):
            main = 'Imp. [Ohm]'
            if re.match('.TR',func):
                sub = 'Theta [rad]'
        header = '{0}, {1}, Stat., Bin no., {2}, meas. start, meas. end'.format(main,sub,sparam)
        return header

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

    def LCR_save(self,LCR_header='',LCR_fpath='test',wa='w'):
        self.LCR.save(fpath=LCR_fpath,header=LCR_header)

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
        NP = 1 # p型のみ搭載
        measure.TFT_IDVGS(ar_name=ar_name,NP=NP,mset=1,Vdd=2.5,Vs=-0.5,Ve=2.5,step=0.1)


    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        measure.close()
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)



