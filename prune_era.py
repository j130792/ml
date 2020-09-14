### Script to prune uninteresting data from the visability data set
# Data reduction will be driven strictly by observed data

import numpy as np
import warnings
from sys import maxsize
import os
try:
    from netCDF4 import Dataset
except:
    os.system('pip3 install netcdf4')
    from netCDF4 import Dataset

if 1/2==0:
    warnings.warn('Script may not be compatible with Python 2',
                  DeprecationWarning)

#Load data globally (as in Era5Vienna.ipynb)
ncfid_1 = Dataset('data/ERA5ViennaData20102014.nc', mode='r') 
ncfid_2 = Dataset('data/ERA5ViennaData20152019.nc', mode='r')
obs_data_vis = np.load('data/VisobsFull.npy')
obs_data_T = np.load('data/TobsFull.npy')
obs_data_Td = np.load('data/TdobsFull.npy')
t2m_1 = ncfid_1['t2m'][:,:,:]-273.15
d2m_1 = ncfid_1['d2m'][:,:,:]-273.15
t2m_2 = ncfid_2['t2m'][:,:,:]-273.15
d2m_2 = ncfid_2['d2m'][:,:,:]-273.15
t2m = np.concatenate((t2m_1,t2m_2), axis=0)
d2m = np.concatenate((d2m_1,d2m_2), axis=0)
Tmodel = np.array(np.reshape(t2m, (-1,4)))
Tdmodel = np.array(np.reshape(d2m, (-1,4)))
Tobs = np.array(obs_data_T[:-7])
Tdobs = np.array(obs_data_Td[:-7])
Visobs = np.array(obs_data_vis[:-7])

#A function which prunes model data subject to deletion index
def PruneModel(dat,DeletionIndex):
    PrunedDat0 = np.delete(dat[:,0],DeletionIndex)
    PrunedDat1 = np.delete(dat[:,1],DeletionIndex)
    PrunedDat2 = np.delete(dat[:,2],DeletionIndex)
    PrunedDat3 = np.delete(dat[:,3],DeletionIndex)

    PrunedDat = np.array([PrunedDat0,PrunedDat1,
                          PrunedDat2,PrunedDat3])

    return PrunedDat
    

def RemoveBoringDay(hrs=24):
    #Check user input is sensible
    if hrs<1 or hrs!=int(hrs):
        raise ValueError('Number of hrs must be a positive integer')
    elif hrs==1:
        warnings.warn('If hrs=1 then every class 7 data point will be removed, to proceed press return')
        input()
        
    DayVisobs = np.zeros((hrs,)) #We define a day to be hrs hours, by default 24 hours
    NumDays = int(np.size(Visobs)/hrs)
    #Locate 'boring days' and add indexes to list for deletion
    DeletionIndex = []
    for day in range(NumDays):
        LocalVisobs = Visobs[day*hrs:day*hrs+hrs]
        if min(LocalVisobs)>=5000:
            DeletionIndex.append(np.arange(hrs*day,hrs*day+hrs))
            
    #Remove entries primed for deletion
    PrunedVisobs = np.delete(Visobs,DeletionIndex)
    PrunedTobs = np.delete(Tobs,DeletionIndex)
    PrunedTmodel = PruneModel(Tmodel,DeletionIndex)
    PrunedTdobs = np.delete(Tdobs,DeletionIndex)
    PrunedTdmodel = PruneModel(Tdmodel,DeletionIndex)

    np.save('data/VisobsFullH%s.npy' % hrs, PrunedVisobs)
    np.save('data/TobsFullH%s.npy' % hrs, PrunedTobs)
    np.save('data/TmodelFullH%s.npy' % hrs, PrunedTmodel)
    np.save('data/TdobsFullH%s.npy' % hrs, PrunedTdobs)
    np.save('data/TdmodelFullH%s.npy' %hrs, PrunedTdmodel)

    return PrunedVisobs


#Function takes a period of specified length and replaces it with one instance
#of maximal visability
def RemoveBoringPeriod(bp=2):
    #Check user input is sensible
    if bp<2:
        raise ValueError('bp must be two or greater for the algorithm to make sense')
    if bp!=int(bp):
        raise ValueError('bp must be an integer')

    #Run algorithm marking indices for deletion
    VisLength = np.size(Visobs)
    DeletionIndex = []
    for i in range(VisLength-bp+1):
        LocalVisobs = Visobs[i:i+bp]
        if min(LocalVisobs)>=5000:
            DeletionIndex.append(np.arange(i+1,i+bp)) #Don't mark first entry for deletion

    #Remove entries primed for deletion
    #(indexes may be marked for deletion multiple times but can only be deleted once)
    PrunedVisobs = np.delete(Visobs,DeletionIndex)
    PrunedTobs = np.delete(Tobs,DeletionIndex)
    PrunedTmodel = PruneModel(Tmodel,DeletionIndex)
    PrunedTdobs = np.delete(Tdobs,DeletionIndex)
    PrunedTdmodel = PruneModel(Tdmodel,DeletionIndex)

    #Save data
    np.save('data/VisobsFullP%s.npy' % bp, PrunedVisobs)
    np.save('data/TobsFullP%s.npy' % bp, PrunedTobs)
    np.save('data/TmodelFullP%s.npy' % bp, PrunedTmodel)
    np.save('data/TdobsFullP%s.npy' % bp, PrunedTdobs)
    np.save('data/TdmodelFullP%s.npy' % bp, PrunedTdmodel)
    
    return PrunedVisobs

#A function which converts a visability into a class
def ClassConverter(vis):
    if vis>=5000:
        Class = 7
    elif vis>=3000:
        Class = 6
    elif vis>=1500:
        Class = 5
    elif vis>=800:
        Class = 4
    elif vis>=600:
        Class = 3
    elif vis>=350:
        Class = 2
    elif vis>=150:
        Class = 1
    else:
        Class = 0
    return Class

#Function will remove instances where we remain in class 7 for more than 1 hour.
#It will also remove all but one instance of adjust classes up to class 7-jump
def RemoveBoringClasses(jump=0):
    #Check user input is sensible
    if jump<0:
        raise ValueError('jump must be zero or greater for the algorithm to make sense')
    elif jump>6:
        raise ValueError('jump is set too high, there are not enough classes for algorithm to make sense')
    if jump!=int(jump):
        raise ValueError('jump must be an integer')

    bp = 2
    #Run algorithm marking indices for deletion
    VisLength = np.size(Visobs)
    DeletionIndex = []
    for i in range(VisLength-bp+1):
        LocalVisobs = Visobs[i:i+bp]
        if min(LocalVisobs)>=5000:
            DeletionIndex.append(np.arange(i+1,i+bp)) #Don't mark first entry for deletion

    #Define a function to remove all but required values from deletion index
    def ReducedIndex(DeletionIndex):

        unique = np.unique(DeletionIndex)
        SubDeletionIndex = []
        
        for i in range(len(unique)-1):
            if unique[i]+1==unique[i+1]:
                SubDeletionIndex.append(i)

        reducedindex = np.delete(unique,SubDeletionIndex)
                
        return reducedindex
            
    ##Recursively check the adjacent class for repeated entries
    #List classes marked for pruning
    Classes = [i+6-jump for i in range(jump,0,-1)]
    for Class in Classes:
        RIndex = ReducedIndex(DeletionIndex)
        for i in RIndex:
            ##Check if two adjacent values to deletion class also need to be deleted
            #Downwind check and mark
            counter = 1
            while 1>0:
                try:
                    minus1 = ClassConverter(Visobs[i-counter])
                    minus2 = ClassConverter(Visobs[i-counter-1])
                except:
                    break
                if (minus1==Class and minus2==Class):
                    DeletionIndex.append([i-counter])
                elif (minus1>Class or minus2>Class):
                    do = -1
                else:
                    break
                counter = counter + 1
            #Upwind check and mark
            counter = 1
            while 1>0:
                try:
                    plus1 = ClassConverter(Visobs[i+counter])
                    plus2 = ClassConverter(Visobs[i+counter+1])
                except:
                    break
                if (plus1==Class and plus2==Class):
                    DeletionIndex.append([i+counter])
                elif (minus1>Class or minus2>Class):
                    do = -1
                else:
                    break
                counter = counter + 1

    #Remove entries primed for deletion
    #(indexes may be marked for deletion multiple times but can only be deleted once)
    PrunedVisobs = np.delete(Visobs,DeletionIndex)
    PrunedTobs = np.delete(Tobs,DeletionIndex)
    PrunedTmodel = PruneModel(Tmodel,DeletionIndex)
    PrunedTdobs = np.delete(Tdobs,DeletionIndex)
    PrunedTdmodel = PruneModel(Tdmodel,DeletionIndex)

    #Save data
    np.save('data/VisobsFullC%s.npy' % bp, PrunedVisobs)
    np.save('data/TobsFullC%s.npy' % bp, PrunedTobs)
    np.save('data/TmodelFullC%s.npy' % bp, PrunedTmodel)
    np.save('data/TdobsFullC%s.npy' % bp, PrunedTdobs)
    np.save('data/TdmodelFullC%s.npy' % bp, PrunedTdmodel)

    return PrunedVisobs

if __name__=="__main__":
    np.set_printoptions(threshold=maxsize) #Allows us to print entire array
    
    out = RemoveBoringDay(24)
    #print(out)
    
    out = RemoveBoringPeriod(2)
    # print(out)

    out = RemoveBoringClasses(1)
    # print(out)
