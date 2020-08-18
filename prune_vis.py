### Script to prune uninteresting data from the visability data set
# Data reduction will be driven strictly by observed data

import sys
import numpy as np
import warnings
np.set_printoptions(threshold=sys.maxsize)

if 1/2==0:
    warnings.warn('Script may not be compatible with Python 2',
                  DeprecationWarning)

#Load data
Visobs = np.load('data/Visobs.npy')
Vismodel = np.load('data/Vismodel.npy')
Tobs = np.load('data/Tobs.npy')
Tmodel = np.load('data/Tmodel.npy')
Tdobs = np.load('data/Tdobs.npy')
Tdmodel = np.load('data/Tdmodel.npy')

#A function which prunes model data subject to deletion index
def PruneModel(dat,DeletionIndex):
    PrunedDat0 = np.delete(dat[0],DeletionIndex)
    PrunedDat1 = np.delete(dat[1],DeletionIndex)
    PrunedDat2 = np.delete(dat[2],DeletionIndex)
    PrunedDat3 = np.delete(dat[3],DeletionIndex)

    PrunedDat = np.array([PrunedDat0,PrunedDat1,
                          PrunedDat2,PrunedDat3])
    
    return PrunedDat
    

def RemoveBoringDay():

    hrs = 24
    DayVisobs = np.zeros((hrs,)) #because 24 hours in a day
    print(DayVisobs.shape)
    NumDays = int(np.size(Visobs)/hrs)
    #Locate 'boring days' and add indexes to list for deletion
    DeletionIndex = []
    for day in range(NumDays):
        LocalVisobs = Visobs[day*24:day*24+24]
        if min(LocalVisobs)>5000:
            DeletionIndex.append(np.arange(24*day,24*day+24))

    #Remove entries primed for deletion
    PrunedVisobs = np.delete(Visobs,DeletionIndex)
    PrunedVismodel = PruneModel(Vismodel,DeletionIndex)
    PrunedTobs = np.delete(Tobs,DeletionIndex)
    PrunedTmodel = PruneModel(Tmodel,DeletionIndex)
    PrunedTdobs = np.delete(Tdobs,DeletionIndex)
    PrunedTdmodel = PruneModel(Tdmodel,DeletionIndex)

    np.save('data/Visobs24.npy',PrunedVisobs)
    np.save('data/Vismodel24.npy',PrunedVismodel)
    np.save('data/Tobs24.npy',PrunedTobs)
    np.save('data/Tmodel24.npy',PrunedTmodel)
    np.save('data/Tdobs24.npy',PrunedTdobs)
    np.save('data/Tdmodel24.npy',PrunedTdmodel)

    print(PrunedVisobs)
    

    return -1



if __name__=="__main__":
    RemoveBoringDay()
