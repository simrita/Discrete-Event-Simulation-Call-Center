# -*- coding: utf-8 -*-
"""
Converted from VBASim by
Yujing Lin, Linda Pei & Barry L Nelson
Last update 8/15/2018
"""

import SimFunctions 
import SimRNG 
import SimClasses
import math
import pandas

ZRNG = SimRNG.InitializeRNSeed()
Calendar = SimClasses.EventCalendar()

RegularQ = SimClasses.FIFOQueue()
SpecialQ = SimClasses.FIFOQueue()
RegularWait = SimClasses.DTStat()
SpecialWait = SimClasses.DTStat()
Regular10 = SimClasses.DTStat()
Special10 = SimClasses.DTStat()
Agents = SimClasses.Resource()
Specialists = SimClasses.Resource()

ARate = []
TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

MeanRegular = 2.5
VarRegular = 1.0
MeanSpecial = 4.0
VarSpecial = 1.0
RunLength = 480
    
NPeriods = 8
Period = 60
MaxRate = 6.24
ARate.append(4.37)
ARate.append(6.24)
ARate.append(5.29)
ARate.append(2.97)
ARate.append(2.03)
ARate.append(2.79)
ARate.append(2.36)
ARate.append(1.04)

TheDTStats.append(RegularWait)
TheDTStats.append(SpecialWait)
TheDTStats.append(Regular10)
TheDTStats.append(Special10)
TheQueues.append(RegularQ)
TheQueues.append(SpecialQ)
TheResources.append(Agents)
TheResources.append(Specialists)


AllRegularWait = []
AllRegularQ = []
AllAgents = []
AllSpecialWait =[]
AllSpecialQ = [] 
AllSpecialists = [] 
AllRegular10 = [] 
AllSpecial10 = [] 
AllClock = []


def NSPP(Stream):
    PossibleArrival = SimClasses.Clock + SimRNG.Expon(1.0/MaxRate, Stream)
    i = int(min(NPeriods, math.ceil(PossibleArrival/Period)))
    while SimRNG.Uniform(0, 1, Stream) >= ARate[i-1]/MaxRate:
        PossibleArrival = PossibleArrival + SimRNG.Expon(1.0/MaxRate, Stream)
        i = int(min(NPeriods, math.ceil(PossibleArrival/Period)))
    nspp = PossibleArrival - SimClasses.Clock
    return nspp
    
    
def Arrival():
    if SimClasses.Clock < RunLength:
        SimFunctions.Schedule(Calendar,"Arrival",NSPP(1))
    else:
        return
    
    Fax = SimClasses.Entity()
    if Agents.Busy < Agents.NumberOfUnits:
        Agents.Seize(1)
        SimFunctions.SchedulePlus(Calendar,"EndOfEntry",SimRNG.Normal(MeanRegular,VarRegular,2),Fax)
    else:
        RegularQ.Add(Fax)
    
    
def SpecialArrival(SpecialFax):
    if Specialists.Busy < Specialists.NumberOfUnits:
        Specialists.Seize(1)
        SimFunctions.SchedulePlus(Calendar,"EndOfEntrySpecial",SimRNG.Normal(MeanSpecial,VarSpecial,4),SpecialFax)
    else:
        SpecialQ.Add(SpecialFax)
        
        
def EndOfEntry(DepartingFax):
    if SimRNG.Uniform(0,1,3) < 0.2:
        SpecialArrival(DepartingFax)
    else:
        Wait = SimClasses.Clock - DepartingFax.CreateTime
        RegularWait.Record(Wait)
        if Wait < 10:
            Regular10.Record(1)
        else:
            Regular10.Record(0)
    
    if RegularQ.NumQueue() > 0 and Agents.NumberOfUnits >= Agents.Busy:
        DepartingFax = RegularQ.Remove()
        SimFunctions.SchedulePlus(Calendar,"EndOfEntry",SimRNG.Normal(MeanRegular,VarRegular,2),DepartingFax)
    else:
        Agents.Free(1)
        
        
def EndOfEntrySpecial(DepartingFax):
    Wait = SimClasses.Clock - DepartingFax.CreateTime
    SpecialWait.Record(Wait)
    if Wait < 10:
        Special10.Record(1)
    else:
        Special10.Record(0)
    
    if SpecialQ.NumQueue() > 0 and Specialists.NumberOfUnits >= Specialists.Busy:
        DepartingFax = SpecialQ.Remove()
        SimFunctions.SchedulePlus(Calendar,"EndOfEntrySpecial",SimRNG.Normal(MeanSpecial,VarSpecial,4),DepartingFax)
    else:
        Specialists.Free(1)



NumAgents = 15
NumAgentsPM = 9
NumSpecialists = 6
NumSpecialistsPM = 3

for reps in range(0,10,1):
    SimFunctions.SimFunctionsInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources)
    Agents.SetUnits(NumAgents)
    Specialists.SetUnits(NumSpecialists)
    SimFunctions.Schedule(Calendar, "Arrival", NSPP(1))
    SimFunctions.Schedule(Calendar, "ChangeStaff", 4*60)
    
    NextEvent = Calendar.Remove()
    SimClasses.Clock = NextEvent.EventTime
 #   print SimClasses.Clock, NextEvent.EventType, NextEvent.WhichObject.CreateTime
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "EndOfEntry":
        EndOfEntry(NextEvent.WhichObject)
    elif NextEvent.EventType == "EndOfEntrySpecial":
        EndOfEntrySpecial(NextEvent.WhichObject)
    elif NextEvent.EventType == "ChangeStaff":
        Agents.SetUnits(NumAgentsPM)
        Specialists.SetUnits(NumSpecialistsPM)
    
    while Calendar.N() > 0:
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
 #       print SimClasses.Clock, NextEvent.EventType, NextEvent.WhichObject
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfEntry":
            EndOfEntry(NextEvent.WhichObject)
        elif NextEvent.EventType == "EndOfEntrySpecial":
            EndOfEntrySpecial(NextEvent.WhichObject)
        elif NextEvent.EventType == "ChangeStaff":
            Agents.SetUnits(NumAgentsPM)
            Specialists.SetUnits(NumSpecialistsPM)
    
    AllRegularWait.append(RegularWait.Mean())
    AllRegularQ.append(RegularQ.Mean())
    AllAgents.append(Agents.Mean())
    AllSpecialWait.append(SpecialWait.Mean())
    AllSpecialQ.append(SpecialQ.Mean())
    AllSpecialists.append(Specialists.Mean())
    AllRegular10.append(Regular10.Mean()) 
    AllSpecial10.append(Special10.Mean()) 
    AllClock.append(SimClasses.Clock)
    
    print reps+1, RegularWait.Mean(), RegularQ.Mean(), Agents.Mean(), SpecialWait.Mean(), SpecialQ.Mean(), Specialists.Mean(), Regular10.Mean(), Special10.Mean(), SimClasses.Clock

AllRegularWait = pandas.DataFrame(AllRegularWait)
AllRegularQ = pandas.DataFrame(AllRegularQ)
AllAgents = pandas.DataFrame(AllAgents)
AllSpecialWait = pandas.DataFrame(AllSpecialWait)
AllSpecialQ = pandas.DataFrame(AllSpecialQ)
AllSpecialists = pandas.DataFrame(AllSpecialists)
AllRegular10 = pandas.DataFrame(AllRegular10)
AllSpecial10 = pandas.DataFrame(AllSpecial10)
AllClock = pandas.DataFrame(AllClock)

#print AllRegularWait.mean(),AllRegularWait.std()
#print AllRegularQ.mean(), AllRegularQ.std()
#print AllAgents.mean(), AllAgents.std()
#print AllSpecialWait.mean(), AllSpecialWait.std()
#print AllSpecialQ.mean(), AllSpecialQ.std()
#print AllSpecialists.mean(), AllSpecialists.std()
#print AllRegular10.mean(), AllRegular10.std()
#print AllSpecial10.mean(), AllSpecial10.std()
#print AllClock.mean(), AllClock.std()