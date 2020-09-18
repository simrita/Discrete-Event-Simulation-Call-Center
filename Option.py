# -*- coding: utf-8 -*-
"""
Converted from VBASim by
Yujing Lin, Linda Pei & Barry L Nelson
Last update 8/15/2018
"""

import SimRNG
import math
import pandas

ZRNG = SimRNG.InitializeRNSeed()
Replications = 10000
Maturity = 1.0
Steps = 32
Sigma = 0.3
InterestRate = 0.05
InitialValue = 50.0
StrikePrice = 55.0
Interval = Maturity / Steps
Sigma2 = Sigma * Sigma / 2

TotalValue = []

for i in range(0,Replications,1):
    Sum = 0.0
    X = InitialValue
    for j in range(0,Steps,1):
        Z = SimRNG.Normal(0,1,12)
        X = X * math.exp((InterestRate - Sigma2) * Interval + Sigma * math.sqrt(Interval) * Z)
        Sum = Sum + X
    Value = math.exp(-InterestRate * Maturity) * max(Sum / Steps - StrikePrice, 0)
    TotalValue.append(Value)    

TotalValue = pandas.DataFrame(TotalValue)

print TotalValue.mean()
print TotalValue.std()