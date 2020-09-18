#!/usr/bin/env python
# coding: utf-8

# In[71]:


import numpy as np
import math
import scipy.stats


# # 0. Load Utilities

# In[72]:


Clock = 0


# In[73]:


class DTStat():
    # Generic discrete-time statistics object

    def __init__(self):
        # Excecutes when the DTStat object is created to initialize variables
        self.Sum = 0.0
        self.SumSquared = 0.0
        self.NumberOfObservations = 0.0
    
    def Record(self,X):
        # Update the DTStat
        self.Sum = self.Sum + X
        self.SumSquared = self.SumSquared + X * X
        self.NumberOfObservations = self.NumberOfObservations + 1
        
    def Mean(self):
        # Return the sample mean
        mean = 0.0
        if self.NumberOfObservations > 0.0:
            mean = self.Sum / self.NumberOfObservations
        return mean

    def StdDev(self):
        # Return the sample standard deviation
        stddev = 0.0
        if self.NumberOfObservations > 1.0:
            stddev = math.sqrt((self.SumSquared - self.Sum**2 / self.NumberOfObservations) / (self.NumberOfObservations - 1))
        return stddev
            
    def N(self):
        # Return the number of observations collected
        return self.NumberOfObservations
    
    def Clear(self):
        # Clear statistics
        self.Sum = 0.0
        self.SumSquared = 0.0
        self.NumberOfObservations = 0.0


# In[74]:


class CTStat():
    # Generic continuous-time statistics object
    # Note that CTStat should be called AFTER the value of the variable changes

    def __init__(self):
        # Excecuted when the CTStat object is created to initialize variables
        self.Area = 0.0
        self.Tlast = 0.0
        self.TClear = 0.0
        self.Xlast = 0.0
        
    def Record(self,X):
        # Update the CTStat from the last time change and keep track of previous value
        self.Area = self.Area + self.Xlast * (Clock - self.Tlast)
        self.Tlast = Clock
        self.Xlast = X

    def Mean(self):
        # Return the sample mean up through the current time but do not update
        mean = 0.0
        if (Clock - self.TClear) > 0.0:
            mean = (self.Area + self.Xlast * (Clock - self.Tlast)) / (Clock - self.TClear)
        return mean
    
    def Clear(self):
        # Clear statistics
        self.Area = 0.0
        self.Tlast = Clock
        self.TClear = Clock


# # 1. Parameters for Simulation

# In[75]:


meanArrival = 1 # mean of arrival time distribution (Exponential)
k_fin= 2 # shape parameter for service time distribution (Gamma)
k_con= 3
meanService = 5
scale_fin = meanService/k_fin
scale_con = meanService/k_con
prob_fin=0.59
prob_renege=0.06
n_servers=7### Number of cross trained Servers. We will change this to see the performance under different number of servers


# # 2. Set up stats

# In[76]:


Wait= DTStat()
Wait_fin= DTStat()
Wait_con= DTStat()


# # 3. Set up servers

# In[77]:


class Resource():
    # This is a generic Resource object that also keeps track of statistics
    # on number of busy resources

    def __init__(self):
        # Executes when the resource object is created to initialize variables
        # and add number of busy Resources statistic to TheCTStats list
        self.Busy = 0
        self.NumberOfUnits = 0
        self.NumBusy = CTStat()
        
    def Seize(self, Units):
        # Seize Units of resource then update statistics
        # Returns False and does not seize if not enouge resources available;
        # otherwise returns True
        diff = self.NumberOfUnits - Units - self.Busy
        if diff >= 0:
            # If diff is nonnegative, then there are enough resources to seize
            self.Busy = self.Busy + Units
            self.NumBusy.Record(float(self.Busy))
            seize = True
        else:
            seize = False
        return seize
        
    def Free(self, Units):
        # Frees Units of resource then update statistics
        # Returns False and does not free if attempting to free more resources than available;
        # otherwise returns True
        diff = self.Busy - Units
        # If diff is negative, then trying to free too many resources
        if diff < 0:
            free = False
        else:
            self.Busy = self.Busy - Units
            self.NumBusy.Record(float(self.Busy))
            free = True
        return free
    
    def Mean(self):
        # Returtime-average number of busy resources up to current time
        return self.NumBusy.Mean()
        
    def SetUnits(self, Units):
        # Set the capacity of the resource (number of identical units)
        self.NumberOfUnits = Units
        
    def Inspect(self):
        # return number of free server(s)
        return self.NumberOfUnits - self.Busy


# In[78]:


Server = Resource()
Server.SetUnits (n_servers) 


# # 4. Set up queue

# In[79]:


class FIFOQueue():
    # This is a generic FIFO Queue object that also keeps track
    # of statistics on the number in the queue (WIP)

    def __init__(self):
        # Executes when the FIFOQueue object is created to add queue statistics
        # to TheCTStats list
        self.WIP = CTStat()
        self.ThisQueue = []
        
    def NumQueue(self):
        # Return current number in the queue
        return len(self.ThisQueue)
        
    def Add(self,X):
        # Add an entity to the end of the queue
        self.ThisQueue.append(X)
        numqueue = self.NumQueue()
        self.WIP.Record(float(numqueue))    
    
    def Remove(self):
        # Remove the first entity from the queue and return the object
        # after updating the queue statistics
        if len(self.ThisQueue) > 0:
            remove = self.ThisQueue.pop(0)
            self.WIP.Record(float(self.NumQueue()))
            return remove
        
    def Mean(self):
        # Return the average number in queue up to the current time
        return self.WIP.Mean()


# In[80]:


Queue = FIFOQueue()


# In[81]:


class CountTracking():
    # This is a generic list keeping track of arrivals/reneges
    
    def __init__(self):
        # Executes when the FIFOQueue object is created to add queue statistics
        # to TheCTStats list
        self.Tracks = []
        
    def Add(self):
        self.Tracks.append(1)
        
    
    def Total(self):
        # Return current number in the queue
        return len(self.Tracks)


# In[82]:


# run this cell to reset after the exercise
Clock = 0
total_arrivals = CountTracking()
total_reneges = CountTracking()


# # 5. Set up calendar

# In[83]:


class EventNotice():
    # This is the generic EventNotice object with EventTime, EventType and 
    # WhichObject attributes
    # Add additional problem-specific attributes here
    def __init__(self):
        self.EventTime = 0.0
        self.EventType = ""
        self.WhichObject = ()


# In[84]:


class EventCalendar():
    # This class creates an EventCalendar object which is a list of
    # EventNotices ordered by time. Based on an object created by Steve Roberts.

    def __init__(self):
        self.ThisCalendar = []   
    def Schedule(self,addedEvent):
        # Add EventNotice in EventTime order
        if len(self.ThisCalendar) == 0:  #no events in calendar
            self.ThisCalendar.append(addedEvent)
        elif self.ThisCalendar[-1].EventTime <= addedEvent.EventTime:
            self.ThisCalendar.append(addedEvent)
        else:
            for rep in range(0,len(self.ThisCalendar),1):
                if self.ThisCalendar[rep].EventTime > addedEvent.EventTime:
                    break
            self.ThisCalendar.insert(rep,addedEvent)
    
    def Remove(self):
        # Remove next event and return the EventNotice object
        if len(self.ThisCalendar) > 0:
            return self.ThisCalendar.pop(0)
        
    def N(self):
        # Return current number of events on the event calendar
        return len(self.ThisCalendar)


# In[85]:


# run this cell to reset after the exercise
Calendar = EventCalendar()


# # 6. Defining the Arrival and Service Functions

# In[86]:


class Entity():
    # This is the generic Entity that has a single attribute CreateTime
    def __init__(self):
        # Executes with the Entity object is created to initialize variables
        # Add additional problem-specific attributes here
        self.CreateTime = Clock
        self.Type=""### Type of Customer- Fin or Con


# In[87]:


def Arrival():
    total_arrivals.Add()
    Schedule(Calendar,EventType = 'Arrival', EventTime = np.random.exponential( meanArrival ))
    u=np.random.uniform(low=0,high=1)
    if u <= prob_fin :
        if Server.Busy < n_servers:
            Server.Seize(1) # If not busy, the server would be occupied now (by calling Seize method).
            Wait.Record(0)
            Wait_fin.Record(0)
            Schedule(Calendar, EventType = 'EndOfService', EventTime = (1.1*np.random.gamma(shape = k_fin, scale = scale_fin)))
        else :
            ren=np.random.uniform(low=0,high=1)
            if ren > prob_renege:
                Customer = Entity()
                Customer.Type = "Fin"
                Queue.Add(Customer)
            else :
                total_reneges.Add()
        
    else:
        if Server.Busy < n_servers:
            Server.Seize(1) # If not busy, the server would be occupied now (by calling Seize method).
            Wait.Record(0)
            Wait_con.Record(0)
            Schedule(Calendar, EventType = 'EndOfService', EventTime = (1.1*np.random.gamma(shape = k_con, scale = scale_con)))
        else :
            ren=np.random.uniform(low=0,high=1)
            if ren > prob_renege:
                Customer = Entity()
                Customer.Type = "Con"
                Queue.Add(Customer)
            else :
                total_reneges.Add()


# In[88]:


def Schedule(calendar,EventType, EventTime):
    #Schedule future events of EventType to occur at time SimClasses.Clock + EventTime
    
    addedEvent = EventNotice()
    addedEvent.EventType = EventType
    addedEvent.EventTime = Clock + EventTime
    # print("SimClasses.Clock is %f" % SimClasses.Clock)
    # print(EventTime)
    calendar.Schedule(addedEvent)


# In[89]:


def EndOfService():
    ### If there is someone in the queue we serve them, else we free the server
    if Queue.NumQueue() > 0:
        DepartingCustomer = Queue.Remove()
        Wait.Record( Clock - DepartingCustomer.CreateTime )
        if DepartingCustomer.Type == "Fin" :
            Wait_fin.Record( Clock - DepartingCustomer.CreateTime )
            Schedule(Calendar, EventType='EndOfService', EventTime=(1.1*np.random.gamma(shape = k_fin, scale = scale_fin)))
        elif DepartingCustomer.Type == "Con" :
            Wait_con.Record( Clock - DepartingCustomer.CreateTime )
            Schedule(Calendar, EventType='EndOfService', EventTime=(1.1*np.random.gamma(shape = k_con, scale = scale_con)))
    else:
        Server.Free(1)


# # 7. run simulation

# In[90]:


# no need to look into the function for now.
# just know that all the stats and components will be reinitialized
# at the beginning of a simulation trial.

def SimFunctionsInit(calendar,queues,ctstats,dtstats,resources):
    # Function to initialize SimFunctions.Python
    # Typically called before the first replication and between replications
    Clock = 0.0
    #Emply event calendar
    while (calendar.N() > 0):
        EV = calendar.Remove()
        
    #Empty queues
    #On first call, append the CStats created by FIFOQueue
    for Q in queues:
        if Q.WIP not in ctstats:
            ctstats.append(Q.WIP)
        while Q.NumQueue() > 0:
            En = Q.Remove()

    #Reinitialize Resources
    #On first call, append the CStats created by FIFOQueue and Resource
    for Re in resources:
        Re.Busy = 0.0
        if Re.NumBusy not in ctstats:
            ctstats.append(Re.NumBusy)  
    
    #Clear statistics
    for CT in ctstats:
        CT.Clear()
        CT.Xlast = 0.0   # added bln 
        
    for DT in dtstats:
        DT.Clear()


# In[92]:


# no need to look into this block.
# just some preparations so that SimFunctionsInit defined above can be called.

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []
TheDTStats.append(Wait)
TheDTStats.append(Wait_fin)
TheDTStats.append(Wait_con)
TheQueues.append(Queue)
TheResources.append(Server)
AllWaitFinMean = []
AllWaitConMean = []
AllWaitMean = []
AllQueueMean = []
AllQueueNum = []
AllServerMean = []
Arrivals = []
Reneges= []


# In[93]:


# For demonstration purpose, let us fix the random seed at this step.
np.random.seed(2020)


# In[94]:


# some parameters for simulation
RunLength = 480 # stop the arrivals if Clock reaches 480 minutes
Clock=0
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h


# In[95]:


max_error = 1
max_errors = []
rep=0
while max_error > 0.05:
    rep=rep+1
    Clock=0
    #===============
    # Initialization
    #===============
    SimFunctionsInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources)
    
    # Two events need to be scheduled.
    # The first arrival,
    # and EndSimulation (so we know when to stop the trial).
    Schedule(Calendar,"Arrival", np.random.exponential(meanArrival) )
    Schedule(Calendar,"EndArrival",RunLength)
    total_arrivals = CountTracking()
    total_reneges = CountTracking()
    
    #================
    # Simulation Loop
    #================
    # First, fetch the next event from the calendar.
    NextEvent = Calendar.Remove()
    # Always remember to UPDATE THE CLOCK when jumping to the next event!
    Clock = NextEvent.EventTime
    
    # Then, depending on the type of the event, call the functions we wrote accordingly.
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "EndOfService":
        EndOfService()
    # the loop: as long as we have not reached the end of simulation,
    # repeat the procedure above.
    while NextEvent.EventType != "EndArrival":
        NextEvent = Calendar.Remove()
        Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfService":
            EndOfService()
        # finish the remaining service
    while len(Calendar.ThisCalendar) !=0:
        NextEvent = Calendar.Remove()
        if NextEvent.EventType == "EndOfService":
            Clock = NextEvent.EventTime
            EndOfService()
    #=============
    # Report Stats
    #=============
    AllWaitMean.append(Wait.Mean())
    AllWaitFinMean.append(Wait_fin.Mean())
    AllWaitConMean.append(Wait_con.Mean())
    AllQueueMean.append(Queue.Mean())
    AllQueueNum.append(Queue.NumQueue())
    AllServerMean.append(Server.Mean())
    Arrivals.append(total_arrivals.Total())
    Reneges.append(total_reneges.Total())
    if rep >= 2:
        error_wait=(mean_confidence_interval(AllWaitMean, confidence=0.95)[0]-mean_confidence_interval(AllWaitMean, confidence=0.95)[1])/mean_confidence_interval(AllWaitMean, confidence=0.95)[0]
        error_queue=(mean_confidence_interval(AllQueueMean, confidence=0.95)[0]-mean_confidence_interval(AllQueueMean, confidence=0.95)[1])/mean_confidence_interval(AllQueueMean, confidence=0.95)[0]
        error_reneges=(mean_confidence_interval(Reneges, confidence=0.95)[0]-mean_confidence_interval(Reneges, confidence=0.95)[1])/mean_confidence_interval(Reneges, confidence=0.95)[0]
        max_error=max(error_wait,error_wait,error_reneges)
        max_errors.append(max_error)


# # 7. View The Results

# In[96]:


mean_confidence_interval(Reneges)


# In[97]:


rep


# In[98]:


mean_confidence_interval(AllWaitMean)


# In[99]:


mean_confidence_interval(AllWaitFinMean)


# In[100]:


mean_confidence_interval(AllWaitConMean)


# In[101]:


mean_confidence_interval(AllQueueMean)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




