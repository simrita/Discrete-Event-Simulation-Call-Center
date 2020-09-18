# -*- coding: utf-8 -*-
"""
Converted from VBASim by
Yujing Lin, Linda Pei & Barry L Nelson
Last update 8/15/2018
"""

import SimRNG
import pandas

ZRNG = SimRNG.InitializeRNSeed()

AllWait = []
print "Rep", "Average Wait"

m = 55000
d = 5000

for Rep in range(0,10,1):
    Y = 0
    SumY = 0
    for i in range(0,d,1):
        a = SimRNG.Expon(1, 1)
        X = SimRNG.Erlang(3, 0.8, 2)
        Y = max(0, Y + X - a)
        
    for i in range(d,m,1):
        a = SimRNG.Expon(1, 1)
        X = SimRNG.Erlang(3, 0.8, 2)
        Y = max(0, Y + X - a)
        SumY = SumY + Y
    AllWait.append(SumY/(float(m-d)))
    print Rep+1, SumY/(float(m-d))

AllWait = pandas.DataFrame(AllWait)


print "Overall Average ", AllWait.mean()
print "Overall Std Dev ", AllWait.std()