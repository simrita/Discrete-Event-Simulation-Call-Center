# -*- coding: utf-8 -*-
"""
Converted from VBASim by
Yujing Lin, Linda Pei & Barry L Nelson
Last update 8/15/2018
"""

import SimClasses
import SimFunctions
import SimRNG
import pandas
 
SimClasses.Clock = 0.0
ZSimRNG = SimRNG.InitializeRNSeed()

Calendar = SimClasses.EventCalendar()
Destination = []
a = 1
b = 2
c = 3
d = 4
InTo = 1
OutOf = 2

Inbound = []
Outbound = []

Nodes = {}

# LP Edits Week 7 Friday 08102018
# These are not defined so I defined them
TheQueues = {}
TheCTStats = {}
TheDTStats = {}
TheResources = {} 

ThisActivity = SimClasses.Activity()
CompletionTime = []

def SANInit():
    global Destination
    global Inbound
    global Outbound
    global Nodes
    global ThisActivity
    
    Destination = []
    Destination.append(b)
    Destination.append(c)
    Destination.append(c)
    Destination.append(d)
    Destination.append(d)
    
    Inbound = []
    Outbound = []
    
    Outbound.append(1)
    Outbound.append(2)
    
    Nodes = {}
    
    # node a
    Nodes[InTo,a] = Inbound
    Nodes[OutOf,a] = Outbound
    Inbound = []
    Outbound = []
    
    # node b
    Inbound.append(1)
    Outbound.append(3)
    Outbound.append(4)
    Nodes[InTo,b] = Inbound
    Nodes[OutOf,b] = Outbound
    Inbound = []
    Outbound = []
    
    # node c
    Inbound.append(2)
    Inbound.append(3)
    Outbound.append(5)
    Nodes[InTo,c] = Inbound
    Nodes[OutOf,c] = Outbound
    Inbound = []
    Outbound = []
    
    # node 5
    Inbound.append(4)
    Inbound.append(5)
    Nodes[InTo,d] = Inbound
    Nodes[OutOf,d] = Outbound
    Inbound = []
    Outbound = []

    ThisActivity = SimClasses.Activity()

def Milestone(ActIn, Node):
    global ThisActivity
    global Inbound
    global Outbound
    global Nodes
    global Destination
    
    Inbound = Nodes[InTo, Node]
    Outbound = Nodes[OutOf, Node]
    m = len(Inbound)
    for Incoming in range(0,m,1):
        if Inbound[Incoming] == ActIn:
            Inbound.remove(Inbound[Incoming])
            break
    Nodes[InTo,Node] = Inbound
    if len(Inbound) == 0:
        m = len(Outbound)
        for ActOut in range(0,m,1):
            ThisActivity = SimClasses.Activity()
            ThisActivity.WhichActivity = Outbound[0]
            ThisActivity.WhichNode = Destination[Outbound[0]-1]
            SimFunctions.SchedulePlus(Calendar,"Milestone", SimRNG.Expon(1,1), ThisActivity)
            Outbound.remove(Outbound[0])
    
for rep in range(0,1000,1):
    SANInit()
    SimFunctions.SimFunctionsInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources)
    Milestone(0,a)
    
    NextEvent = Calendar.Remove()
    SimClasses.Clock = NextEvent.EventTime
    ThisActivity = NextEvent.WhichObject
    Milestone(ThisActivity.WhichActivity,ThisActivity.WhichNode)
    
    while Calendar.N() > 0:
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
        ThisActivity = NextEvent.WhichObject
        Milestone(ThisActivity.WhichActivity,ThisActivity.WhichNode)
    
    CompletionTime.append(SimClasses.Clock)
    # print SimClasses.Clock
    
CompletionTime = pandas.DataFrame(CompletionTime)
print(CompletionTime.mean())