# -*- coding: utf-8 -*-
"""
Converted from VBASim by
Yujing Lin, Linda Pei & Barry L Nelson
Last update 8/15/2018
"""


import SimClasses
import SimFunctions
import SimRNG
import math
import pandas
 
SimClasses.Clock = 0
MeanParkingTime = 2.0
QueueLength = SimClasses.CTStat()
N = 0
MaxQueue = 0

ZSimRNG = SimRNG.InitializeRNSeed()
Calendar = SimClasses.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

TheCTStats.append(QueueLength)

AllQueueLength = []
AllMaxQueue = []
AllN = []

print("Average Number in Queue", "Maximum Number in Queue")
 
def NSPP(Stream):
    PossibleArrival = SimClasses.Clock + SimRNG.Expon(1.0/110, Stream)
    while SimRNG.Uniform(0, 1, Stream) >= (100 + 10 * math.sin(3.141593 * PossibleArrival / 12)) / 110.0:
        PossibleArrival = PossibleArrival + SimRNG.Expon(1.0/110, Stream)
    nspp = PossibleArrival - SimClasses.Clock
    return nspp

def Arrival():
    global MaxQueue
    global N
    interarrival = NSPP(1)
    SimFunctions.Schedule(Calendar,"Arrival", interarrival)
    N = N + 1
    QueueLength.Record(N)
    if N > MaxQueue:
        MaxQueue = N   
    SimFunctions.Schedule(Calendar,"Departure",SimRNG.Expon(MeanParkingTime, 2))

def Departure():
    global N
    N = N - 1
    QueueLength.Record(N)
    
for Reps in range(0,20,1):
    N = 0
    MaxQueue = 0
    SimFunctions.SimFunctionsInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources)
    interarrival = NSPP(1)
    SimFunctions.Schedule(Calendar,"Arrival",interarrival)
    SimFunctions.Schedule(Calendar,"EndSimulation", 24)
    
    NextEvent = Calendar.Remove()
    SimClasses.Clock = NextEvent.EventTime
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "Departure":
        Departure()
    
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "Departure":
            Departure()
    
    AllQueueLength.append(QueueLength.Mean())
    AllMaxQueue.append(MaxQueue)
    AllN.append(N) 
    
    print(Reps+1, QueueLength.Mean(), MaxQueue, N)

output = {"AllQueueLength" : AllQueueLength, "AllMaxQueue": AllMaxQueue, "AllN" : AllN}
output = pandas.DataFrame(output)
output.to_csv("MMInfinity_output.csv", sep=",")
 
AllQueueLength = pandas.DataFrame(AllQueueLength)
AllMaxQueue = pandas.DataFrame(AllMaxQueue)
AllN = pandas.DataFrame(AllN) 

print(AllQueueLength.mean())
print(AllQueueLength.std())
print(AllMaxQueue.mean())
print(AllMaxQueue.std())
print(AllN.mean())
print(AllN.std())
