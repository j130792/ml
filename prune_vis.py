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
        LocalVisobs = Visobs[day*hrs:day*hrs+hrs]
        if min(LocalVisobs)>5000:
            DeletionIndex.append(np.arange(hrs*day,hrs*day+hrs))
            
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
    PrunedVismodel = PruneModel(Vismodel,DeletionIndex)
    PrunedTobs = np.delete(Tobs,DeletionIndex)
    PrunedTmodel = PruneModel(Tmodel,DeletionIndex)
    PrunedTdobs = np.delete(Tdobs,DeletionIndex)
    PrunedTdmodel = PruneModel(Tdmodel,DeletionIndex)

    #Save data
    np.save('data/VisobsP%s.npy' % bp, PrunedVisobs)
    np.save('data/VismodelP%s.npy' % bp, PrunedVismodel)
    np.save('data/TobsP%s.npy' % bp, PrunedTobs)
    np.save('data/TmodelP%s.npy' % bp, PrunedTmodel)
    np.save('data/TdobsP%s.npy' % bp, PrunedTdobs)
    np.save('data/TdmodelP%s.npy' % bp, PrunedTdmodel)
    
    print(PrunedVisobs)
                    


if __name__=="__main__":
    RemoveBoringPeriod(2)
