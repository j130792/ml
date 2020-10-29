"""
Add raw missing visability data
"""

import numpy as np
import csv
from datetime import datetime, timedelta


#Define the maximum for the ceiling variable
ceiling_max = 30000

#This function shifts the date forward by X minutes
def time_shifter(t,add_mins):

    t = t + timedelta(minutes=30)

    t = t.strftime('%Y-%m-%d %H:%M')
        
    return t

def float_time(t):
    t = datetime.strptime(t, '%Y-%m-%d %H:%M')
    return t.timestamp()

def read_time(secs):
    return datetime.fromtimestamp(secs).strftime('%Y-%m-%d %H:%M')


## Read CVS file
f = open('data/LOWW_metar_2009_to_2020.csv')
csv_f = csv.reader(f)

headers = ['time', 'location', 'QHN', 'Temperature',
           'Dewpoint','Visibility', 'WindDirection',
           'WindSpeed','Gusts','RVR','Weather',
           'Ceiling']
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

i = 0
for row in csv_f:
    if i==0:
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
    elif i==1:
        t_old = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
        time.append(row[0])
        location.append(row[1])
        QHN.append(row[2])
        Temperature.append(row[3])
        Dewpoint.append(row[4])
        Visibility.append(row[5])
        try:
            WDN = str(float(row[6]))
        except:
            WDN = str(0)
        WindDirection.append(WDN)
        WindSpeed.append(row[7])
        Gusts.append(row[8])
        RVR.append(row[9])
        Weather.append(row[10])
        Ceiling.append(row[11])
    else:
        t = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
        t_diff = int((t-t_old).total_seconds()/60.0)
        # We can also implement the interpolation utilising numpy!!
        #Interpolate relevant data as floats
        t1 = float_time(row[0])
        t0 = float_time(time[-1])
        num_points = int(t_diff/30)
        t_points = np.linspace(t0,t1,num_points)
        t_known = [t0,t1]
        temp_known = [float(Temperature[-1]),float(row[3])]
        temp_interp = np.interp(t_points,t_known,temp_known)
        dew_known = [float(Dewpoint[-1]),float(row[4])]
        dew_interp = np.interp(t_points,t_known,dew_known)
        vis_known = [float(Visibility[-1]),float(row[5])]
        vis_interp = np.interp(t_points,t_known,vis_known)
        WDN = str(row[6])
        try:
            WDN2 = float(WDN)
        except:
            WDN2 = 0
        windd_known = [float(WindDirection[-1]),float(WDN2)]
        windd_interp = np.interp(t_points,t_known,windd_known)
        WindSpeedNew = row[7]
        if WindSpeedNew==None:
            WindSpeedNew = 0
        winds_known = [float(WindSpeed[-1]),float(row[7])]
        winds_interp = np.interp(t_points,t_known,winds_known)
        
        #Append interpolated data as strings
        for i in range(num_points):
            time.append(str(read_time(t_points[i])))
            location.append(str(row[1]))
            QHN.append(str(row[2]))
            Temperature.append(str(temp_interp[i]))
            Dewpoint.append(str(dew_interp[i]))
            Visibility.append(str(vis_interp[i]))
            WindDirection.append(str(windd_interp[i]))
            WindSpeed.append(str(winds_interp[i]))
            Gusts.append(str(row[8]))
            RVR.append(str(row[9]))
            Weather.append(str(row[10]))
            Ceiling.append(str(row[11])) #Not currently being handled correctly
            
    if i>1:
        t_old = t
    i+=1
    

##Write CVS file
Data = []
for i in range(len(time)):
    Data.append([time[i],location[i],QHN[i],
                 Temperature[i],Dewpoint[i],
                 Visibility[i],WindDirection[i],
                 WindSpeed[i],Gusts[i],RVR[i],
                 Weather[i],Ceiling[i]])

F = open('output/vis_full.csv','w')
with F:
    writer = csv.writer(F)
    writer.writerows(Data)

print('Writing complete')
