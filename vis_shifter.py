"""
Add raw missing visability data
"""

import numpy as np
import csv
from datetime import datetime, timedelta

import matplotlib.pylab as plt

#This function shifts the date forward by X minutes
def time_shifter(t,add_mins):

    t = t + timedelta(minutes=30)

    t = t.strftime('%Y-%m-%d %H:%M')
        
    return t

def float_time(t):
    t = datetime.strptime(t, '%Y-%m-%d %H:%M')
    return t.timestamp()

def read_time(secs):
    t = datetime.fromtimestamp(secs)
    t = roundTime(t).strftime('%Y-%m-%d %H:%M')
    return t

def roundTime(dt, roundTo=60):
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + timedelta(0,rounding-seconds,-dt.microsecond)


## Read CVS file
try:
    f = open('output/vis_full.csv')
except:
    raise ValueError('vis_full.csv does not exist, please run vis_interpolator')

csv_f = csv.reader(f)

#Set up empty lists to repopulate data
time = []
location = []
QHN = []
Temperature = []
Dewpoint = []
Visibility = []
WindDirection = []
WindSpeed = []
Gusts = []
RVR = []
Weather = []
Ceiling = []

#Save data in arrays as floats
i = 0
for row in csv_f:
    if i<0:#do not enter for now
        time.append(row[0])
        location.append(row[1])
        QHN.append(row[2])
        Temperature.append(row[3])
        Dewpoint.append(row[4])
        Visibility.append(row[5])
        WindDirection.append(row[6])
        WindSpeed.append(row[7])
        Gusts.append(row[8])
        RVR.append(row[9])
        Weather.append(row[10])
        Ceiling.append(row[11])
    elif i>0:
        time.append(float(float_time(row[0])))
        location.append(row[1])
        QHN.append(row[2])
        Temperature.append(float(row[3]))
        Dewpoint.append(float(row[4]))
        Visibility.append(float(row[5]))
        WindDirection.append(float(row[6]))
        WindSpeed.append(float(row[7]))
        Gusts.append(row[8])
        RVR.append(row[9])
        Weather.append(row[10])
        Ceiling.append(float(row[11]))
            
    i=i+1

#Set up relevant interpolants, sample 10 minute intervals
t_fine = np.linspace(t0,t1,3*len(time))
temp_fine = np.interp(t_fine,time,Temperature)
dew_fine = np.interp(t_fine,time,Dewpoint)
vis_fine = np.interp(t_fine,time,Visibility)
windd_fine = np.interp(t_fine,time,WindDirection)
winds_fine = np.interp(t_fine,time,WindSpeed)
ceil_fine = np.interp(t_fine,time,Ceiling)

#Grab the data every 30 minutes on the half hour
time_out = []
location_out = []
QHN_out = []
Temperature_out = []
Dewpoint_out = []
Visibility_out = []
WindDirection_out = []
WindSpeed_out = []
Gusts_out = []
RVR_out = []
Weather_out = []
Ceiling_out = []
i = 0
for i in range(len(time)):
    index = 3*i+1
    time_out.append(str(read_time(t_fine[index])))
    location_out.append(row[1])
    QHN_out.append(row[2])
    Temperature_out.append(str(temp_fine[index]))
    Dewpoint_out.append(str(dew_fine[index]))
    Visibility_out.append(str(vis_fine[index]))
    WindDirection_out.append(str(windd_fine[index]))
    WindSpeed_out.append(str(winds_fine[index]))
    Gusts_out.append(row[8])
    RVR_out.append(row[9])
    Weather_out.append(row[10])
    Ceiling_out.append(str(ceil_fine[index]))

    i = i + 1



##Write CVS file
Data = []
Data.append(['Time','Location','QNH','Temperature','Dewpoint','Visibility',
             'WindDirection','WindSpeed','Gusts','RVR','Weather','Ceiling'])
i = 0
for i in range(len(time)):
    Data.append([time_out[i],location_out[i],QHN_out[i],
                 Temperature_out[i],Dewpoint_out[i],
                 Visibility_out[i],WindDirection_out[i],
                 WindSpeed_out[i],Gusts_out[i],RVR_out[i],
                 Weather_out[i],Ceiling_out[i]])
    i = i + 1

F = open('output/vis_shifted.csv','w')
with F:
    writer = csv.writer(F)
    writer.writerows(Data)

print('Writing complete')
