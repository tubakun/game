# -*- coding:utf-8 -*-

import pyvisa as visa

rm = visa.ResourceManager()
e5270 = rm.open_resource(str('GPIB0::9::INSTR'))
idn = e5270.query("*IDN?")
print (idn)
e5270.write("*RST")
e5270.timeout=100000

e5270_2 = rm.open_resource(str('GPIB2::17::INSTR'))
idn = e5270_2.query("*IDN?")
print (idn)
e5270_2.write("*RST")
e5270_2.timeout=100000

e5270.write('DZ')
e5270_2.write('DZ')