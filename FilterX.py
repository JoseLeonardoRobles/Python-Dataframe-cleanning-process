from __future__ import (absolute_import, division, print_function,unicode_literals)
'''
====================================================================================================================
Universidad Complutense de Madrid
Astrophysics' Department
Ph.D.'s Project: To Statistical Study the Night Sky Brightness and Color Evolution in Madrid.
Supervisors: PhD. Jaime Zamorano and Sergio Pascual
Python 3.6 version: Jose Robles, Ph.D. student 
email: josrob01@ucm.es

Tasks: 1_To generate .csv files
       2_To generate a .csv color file (Correlative colors B-V-R)
       3_To plot ASTMON, SQM_LE/LU, and TESS (Nightly)
       4_To classify data according to  moon phases (FilterX): Astropy > IERS Bulletin A table > maia.usno.navy
       5_To classify data according to cloud coverage (FilterX): expert decision filtering making
====================================================================================================================
'''
'''
=======================
1] LIBRARIES
=======================
''' 
import numpy as np
import pytz
import os
import astropy 
from astropy.time import Time
from astropy.coordinates import get_moon, get_sun
import astroplan
from astroplan import Observer,download_IERS_A
import astropy.units as u
from astropy.coordinates import EarthLocation
from astropy.table import Table
import pandas as pd
from pandas.api.types import CategoricalDtype
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
import datetime
import matplotlib.dates as mdates
import operator
from operator import itemgetter
import subprocess
import time
matplotlib.style.use('ggplot')
'''
=======================
2] OBSERVATORY COORDINATES 
=======================
''' 
#download_IERS_A()
location = EarthLocation.from_geodetic(-3.726065*u.deg, 40.450941*u.deg, 650*u.m)
UCM = Observer(location=location, name="UCM_OBS")
'''
=======================
2.x] DATA ACQUISITION: SUB-PROCESS 
=======================
''' 
#subprocess.Popen(['open',  '-W', '-n','-a', "/System/Library/CoreServices/Applications/Screen Sharing.app"]) 

'''
cols_names = ['Datetime','Pixel_x','Pixel_y','Magnitudes','Error','Pos_0','w']
data = pd.read_table('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/ASTMON/UCM-B-Pos0-20170401-20180926.dat',sep ='\s+',header=None, names=cols_names)
data.drop(['w'],axis=1,inplace=True)
dates = data.Datetime.str.split('_').apply(lambda x:x[0])
time = data.Datetime.str.split('_').apply(lambda x:x[1])
data['Datetime_Format1'] = dates + time
data['Datetime_Format1'] = d = pd.to_datetime(data['Datetime_Format1'])
data.set_index('Datetime_Format1', inplace = True)# ephem, Astropy and Pandas (Setting an index)
data['Datetime_Format1'] = data.index
data['Julian_Dates']= data.index.to_julian_date()
data['Pos_0'] = 'Pos0'
data['Johnson_Filter'] = 'Johnson-B'
data = data.round({'Magnitudes': 2, 'Error':2, 'Julian_Dates': 8}) # Ask to the expert, show the example with 3 and 4//ephem and Astropy suggested 8 digits
data.dropna(how='any')
DI = data.info(memory_usage='deep')
data = data[['Julian_Dates','Datetime','Datetime_Format1','Johnson_Filter','Pos_0','Pixel_x','Pixel_y','Magnitudes','Error']]

#2.1] Detecting Outliners and creating .csv file
DS = data.describe()
print(DS)
print(data)
data.to_csv('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/ASTMON/UCM-B-Pos0-20170401-20180926.csv',index=False, header=False,sep =';')
'''

'''
=======================
3] ASTMON DATA FRAME, CLEANING PROCESS, AND COLOR INDEX
=======================
''' 
#3.1] ASTMON'S DATA FRAME
ASTMON_cols_names = ['Julian_Dates','Datetime','Datetime_Format1','Filter','Pos_0','Pixel_x','Pixel_y','Magnitudes','Error']
ASTMON = pd.read_csv('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/Z_ASTMON_Output/Z_ucm-colores_20170401_20180926/UCM-colores_20170401_20180926.csv',header=None, names = ASTMON_cols_names,sep =';')
ASTMON['Julian_Dates'] = ASTMON.Julian_Dates.astype('float')
ASTMON['DataQuality_Flag'] =1
ASTMON['DataQuality_Flag'] =ASTMON.DataQuality_Flag.astype('category')
cat_type = CategoricalDtype(categories=list('BVR'),ordered=True)# Controlling category behavior 
ASTMON['Filter_codes']=ASTMON.Filter.str.split('-').apply(lambda x:x[1])#.astype('category')
ASTMON['Filter_codes']=ASTMON['Filter_codes'].astype(cat_type)
ASTMON['Datetime_Format1'] = pd.to_datetime(ASTMON['Datetime_Format1'],utc=True)
ASTMON['Pos_0'] =ASTMON.Pos_0.astype('category')
ASTMON['Pixel_x'] =ASTMON.Pixel_x.astype('category')
ASTMON['Pixel_y'] =ASTMON.Pixel_y.astype('category')
ASTMON['Error'] =ASTMON.Error.astype('category')
ASTMON['Colors'] = ASTMON.DataQuality_Flag.map({0:'Poor data quality_Cloudy',1:'Good data quality_No moon_no clouds',2:'Good data quality_Moon_No clouds'})
ASTMON['Colors'] = ASTMON.Colors.astype('category')# Improve efficiency  
#dates = ASTMON.Datetime.str.split('_').apply(lambda x:x[0])
#time = ASTMON.Datetime.str.split('_').apply(lambda x:x[1])

#3.2] CLEANING PROCESS
ASTMON.dropna(how='any')
ASTMON.set_index('Datetime_Format1', inplace = True)
ASTMON['Filter_codesNumber']=ASTMON['Filter_codes'].cat.codes# pulling out codes behind Filter_codes
ASTMON.info(memory_usage='deep')
print(ASTMON.describe())
print(ASTMON)

#3.3] COLOR INDEX: CREATE A DATA FRAME 

#WARNING: RUN THIS CODE AFTER THE ACQUISITION OF NEW DATA 
'''pattern = [0,1,2]
matched = ASTMON.rolling(len(pattern)).apply(lambda x: all(np.equal(x,pattern)))#.astype(bool)
matched = matched.sum(axis = 1).astype(bool)
indx_matched = np.where(matched)[0]
subset = [range(match-len(pattern)+1, match+1) for match in indx_matched]
print(matched)
print(len(matched))
result = pd.concat([ASTMON.iloc[subs,:] for subs in subset],axis=0)
print(result)
result.info(memory_usage='deep')
result.to_csv('/Users/joserobles/Desktop/UCM-colores_INDEX_20170401_20180926.csv',index=True, header=True,sep =';')'''

'''
=======================
4] SQM_LE DATA FRAME AND CLEANING PROCESS 
=======================
''' 
#4.1] SQM_LE_DATA FRAME
SQM_LE_cols_names = ['Datetime_Format1','Datetime_F2_LE','Temp_sensor','D','Freq','Mag']
SQM_LE = pd.read_csv('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/SQM/SQM_LE/data_UCM-SQM-LE-1952_2017_2018.csv',header = None, names = SQM_LE_cols_names, sep =';',low_memory=False)
SQM_LE.drop(['Temp_sensor','D','Freq','Datetime_F2_LE'],axis=1,inplace=True)

#4.1.2] CLEANING PROCESS
SQM_LE.Mag >= 14 #14
SQM_LE = SQM_LE[SQM_LE.Mag >= 14]# Cut-off: 14 mag/arsec^2
SQM_LE.Mag <= 19 #18
SQM_LE = SQM_LE[SQM_LE.Mag <= 19]
SQM_LE['Datetime_Format1'] = pd.to_datetime(SQM_LE['Datetime_Format1'],utc=True)
SQM_LE.set_index('Datetime_Format1',inplace=True)
SQM_LE['DataQuality_Flag'] = 1
SQM_LE['DataQuality_Flag'] = SQM_LE.DataQuality_Flag.astype('category')
SQM_LE['Mag'] = SQM_LE.Mag.astype('float')
SQM_LE.dropna(how='any')
SQM_LE.info(memory_usage='deep')
print(SQM_LE.describe())
print(SQM_LE)

'''
=======================
5] SQM_LU DATA FRAME AND DATA CLEANING PROCESS 
=======================
''' 

#5.1] SQM_LU_DATA FRAME
SQM_LU_cols_names = ['Datetime_Format1','Datetime_F2_LU','Temp','Counts','Freq','Mag']
SQM_LU = pd.read_csv('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/SQM/SQM_LU/data_UCM-SQM-LU-2218_2017_2018.csv',header =None,sep=';',names=SQM_LU_cols_names)
SQM_LU.drop(['Datetime_F2_LU','Temp','Freq','Counts'],axis=1,inplace=True)
SQM_LU['DataQuality_Flag'] =1
SQM_LU['DataQuality_Flag'] = SQM_LU.DataQuality_Flag.astype('category')

#5.1.2] CLEANING PROCESS
SQM_LU.Mag >= 14
SQM_LU = SQM_LU[SQM_LU.Mag >= 14]# Cut-off: 14 mag/arsec^2
SQM_LU.Mag <=19
SQM_LU = SQM_LU[SQM_LU.Mag <= 19]
SQM_LU['Datetime_Format1'] = pd.to_datetime(SQM_LU['Datetime_Format1'],utc=True)
SQM_LU.set_index('Datetime_Format1',inplace=True)
SQM_LU.dropna(how='any')
SQM_LU.info(memory_usage='deep')
print(SQM_LU.describe())
print(SQM_LU)

'''
=======================
6] TESS-W DATA FRAME AND DATA CLEANING PROCESS 
=======================
''' 
#6.1] TESS_DATA FRAME
TESS_cols_names = ['Datetime_Format1','Datetime_F2','Temp_sensor','Freq','Mag','ZP']# intro zp formula
TESS = pd.read_csv('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/TESS/data_TESS-stars5_UCM_up_to_201809.csv',header =None,sep=';',names=TESS_cols_names)
TESS.drop(['Datetime_F2','Temp_sensor','Freq','ZP'],axis=1,inplace=True)
TESS['DataQuality_Flag'] =1
TESS['DataQuality_Flag'] = TESS.DataQuality_Flag.astype('category')

#6.1.2] CLEANING PROCESS
TESS.Mag >= 14
TESS = TESS[TESS.Mag >= 14]# Cut-off: 14 mag/arsec^2
TESS.Mag <=19
TESS = TESS[TESS.Mag <= 19]
TESS['Datetime_Format1'] = pd.to_datetime(TESS['Datetime_Format1'],utc=True)
TESS.set_index('Datetime_Format1',inplace=True)
TESS.dropna(how='any')
TESS.info(memory_usage='deep')
print(TESS.describe())
print(TESS)

'''
=======================
7] ASTMON'S COLOR INDEX DATA FRAME 
=======================
''' 
#7.1] BVR'S DATA FRAME WITH RECTIFIED PATTERNS  
CHUNKS_names = ['Datetime_Format1','Julian_Dates','Datetime','Filter','Pos_0','Pixel_x','Pixel_y','Magnitudes','Error','DataQuality_Flag','Filter_codes','Colors','Filter_codesNumber']
ASTMONCHUNK = pd.read_csv('/Users/joserobles/Desktop/python3/Samples/UCM_PhD_Project/ASTMON_Output/UCM_ASTMON_INDEX_20170401_20180926.csv',header = 0,sep =';',index_col='Datetime_Format1',names=CHUNKS_names)
ASTMONCHUNK.drop(['Julian_Dates','Datetime','Filter','Pos_0','Pixel_x','Pixel_y','Error','DataQuality_Flag','Colors','Filter_codesNumber'],axis=1,inplace=True)
ASTMONCHUNK['Filter_codes'] = ASTMONCHUNK.Filter_codes.astype('category')
ASTMONCHUNK.info(memory_usage='deep')
print(ASTMONCHUNK.describe())
print(ASTMONCHUNK)

#7.2] COLOR INDEX: DATA FRAME DERIVED FROM ASTMONCHUNK  

#7.2.1 PROCESS 1: SPLITTING PHOTOMETRIC BANDS
ASTMONCHUNK = ASTMONCHUNK.groupby('Filter_codes')
mB = ASTMONCHUNK.get_group('B')
mV = ASTMONCHUNK.get_group('V')
mR = ASTMONCHUNK.get_group('R')

#7.2.3 PROCESS 2: APPLYING A SUBSTRACTION TO GET THE INDEXES
INDEX1 = (mB['Magnitudes'].values) - (mV['Magnitudes'].values)
INDEX2 = (mV['Magnitudes'].values) - (mR['Magnitudes'].values)

#7.2.3.1 RESETING, CONVERTING, AND SETTING INDEX
mV = mV.reset_index()
mV['Datetime_Format1'] = pd.to_datetime(mV['Datetime_Format1'],utc=True)
mV.set_index('Datetime_Format1',inplace=True)

#7.2.4 PROCESS 3: COMBINING INDEXES WITH V'S BANDS TIMESTAMP 
df1 = pd.DataFrame(INDEX1,index=mV.index,columns=['mB-mV'])
df2 = pd.DataFrame(INDEX2,index=mV.index,columns=['mV-mR'])
ASTMONINDEX = pd.concat([df1,df2],axis=1)
ASTMONINDEX.info(memory_usage='deep')
print(ASTMONINDEX.describe())
print(ASTMONINDEX)
'''
=======================
8] ASTMON SORTING VALUES IN DICTIONARIES  
=======================
'''
#WARNING: 1) Python3.6 does not allow to order a dictionary. Instead, is better to sort a list of tuples
       #  2) Python3.7 allow to order a dictionary

#8.1] SORTING VALUES IN DICTIONARIES
first = {'B':'b','V':'g','R':'r'} 
set_colors = first.values()
sorted_first = sorted(first.items(), key=operator.itemgetter(1))#Sort the keys and values as a list of tuples.
print(sorted_first)
second = {1:2,2:4,0:3}# {[Modifies Moon over horizon size],[Modifies Poor data Quality size],[Modifies good data quality size]}
sorted_second = sorted(second.items(),key = operator.itemgetter(1))
print(sorted_second)# [Good data quality_Moon_No clouds] ,[Good data quality_No moon_no clouds]
third={'Good data quality_Moon_No clouds':'white','Good data quality_No moon_no clouds':'8','Poor data quality_Cloudy':'black'} 
sorted_third = sorted(third.items(), key = operator.itemgetter(1))
print(sorted_third)
first.update(second)# Combines dictionaries

'''
=======================
9] ASTMON,SQM_LE,SQM_LU, and TESS VISUALIZATION BY COLORS AND NIGHT SKY CONDITIONS 
=======================
'''
#9.1] ASTMON AND ASTMON'S INDEXES: TIME LIMIT WITH NUMPY FLAVOUR
start = datetime.datetime.strptime('2017-04-01 15:00:00',"%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime('2017-04-02 05:00:00',"%Y-%m-%d %H:%M:%S")
delta = datetime.timedelta(days=1)

#9.2] SQM_LE
SQM_LE_Start = datetime.datetime.strptime('2017-04-01 15:00:00',"%Y-%m-%d %H:%M:%S")
SQM_LE_end = datetime.datetime.strptime('2017-04-02 06:00:00',"%Y-%m-%d %H:%M:%S")
SQM_LE_delta = datetime.timedelta(days=1)

#9.3] SQM_LU
SQM_LU_Start = datetime.datetime.strptime('2017-04-01 15:00:00',"%Y-%m-%d %H:%M:%S")
SQM_LU_end = datetime.datetime.strptime('2017-04-02 06:00:00',"%Y-%m-%d %H:%M:%S")
SQM_LU_delta = datetime.timedelta(days=1)

#9.4] TESS-W
TESS_Start = datetime.datetime.strptime('2017-04-01 15:00:00',"%Y-%m-%d %H:%M:%S")
TESS_end = datetime.datetime.strptime('2017-04-02 06:00:00',"%Y-%m-%d %H:%M:%S")
TESS_delta = datetime.timedelta(days=1)

#DAYS= 6
#9.5] ASTMON'S MASK WITH NUMPY 
#PLEASE TYPE AN INTEGER TO DEFINE THE DAYS  
DAYS=1
for i in range(DAYS):
    print(start,end)
    start = start + delta
    end = end + delta
    mask = (ASTMON.index >= start) & (ASTMON.index < end)
    print(mask)

#9.5.1] ASTMON'S INDEX
for m in range(DAYS):
    print(start,end)
    mask_Index = (ASTMONINDEX.index >= start) & (ASTMONINDEX.index < end)
    print(mask_Index)
    

#9.6] SQM_LE
for j in range(DAYS):
    print(SQM_LE_Start,SQM_LE_end)
    SQM_LE_Start = SQM_LE_Start + SQM_LE_delta
    SQM_LE_end = SQM_LE_end + SQM_LE_delta
    SQM_LE_mask = (SQM_LE.index >= SQM_LE_Start) & (SQM_LE.index < SQM_LE_end)
    print(SQM_LE_mask)
    print(SQM_LE.loc[SQM_LE_mask])

#9.7] SQM_LE 
for k in range(DAYS):
    print(SQM_LU_Start,SQM_LU_end)
    SQM_LU_Start = SQM_LU_Start + SQM_LU_delta
    SQM_LU_end = SQM_LU_end + SQM_LU_delta
    SQM_LU_mask = (SQM_LU.index >= SQM_LU_Start) & (SQM_LU.index < SQM_LU_end)
    print(SQM_LU_mask)
    print(SQM_LU.loc[SQM_LU_mask])

#9.8] TESS-W
for l in range(DAYS):
    print(TESS_Start,TESS_end)
    TESS_Start = TESS_Start + TESS_delta
    TESS_end = TESS_end + TESS_delta
    TESS_mask = (TESS.index >= TESS_Start) & (TESS.index < TESS_end)
    print(TESS_mask)
    print(TESS.loc[TESS_mask])

#9.8] APPARATUSES' PLOTS: PHOTOMETRIC NIGHTS (NO CLOUDS AND NO MOON)
for key, group in ASTMON[mask].groupby(['Filter_codes'],as_index=True,axis=0).Magnitudes:
    key_clean = key[0].strip()
    plt.title('Magnitudes vs Time', color='black')
    plt.ylabel('Magnitudes(mag/arcsec^2)')
    plt.title('Magnitudes vs Time', color='black')
    plt.legend([start.year,'ASTMON_B','ASTMON_V','ASTMON_R','SQM_LE(Black)','SQM_LU(Grey)','TESS-W(Magenta)'],loc='best',fancybox=True,framealpha=0.3)
    #plt.legend(['2017','ASTMON_B','ASTMON_V','ASTMON_R','SQM_LE(Black)','SQM_LU(Grey)','TESS-W(Magenta)'],loc='best',fancybox=True,framealpha=0.3)
    group.plot(y='Magnitudes',style ='o',rot=45,c=first[key_clean],alpha=0.9,subplots=True,markersize=0.9,figsize=(12,8))
    SQM_LE[SQM_LE_mask].Mag.plot(style='o',c='black',subplots=True,markersize=0.5,figsize=(12,8))
    SQM_LU[SQM_LU_mask].Mag.plot(style='o',c='grey',subplots=True,markersize=0.5,figsize=(12,8))
    TESS[TESS_mask].Mag.plot(style='o',c='m',markersize=0.5,figsize=(12,8))

plt.tight_layout()
plt.show()

'''
=======================
10] APPARATUSES' VISUALIZATION BY COLORS AND NIGHT SKY CONDITIONS WITH FILTER-F (MANUAL FILTER: EXPERT FILTERING DECISION MAKING)
=======================
'''

#10.x] READING APPARATUSES DATA FRAME: 1) ASTMON, 2) SQM-LE, 3) SQM-LU, AND 4) TESS
ASTMONF = pd.read_csv('/Users/joserobles/Desktop/python3/Samples/UCM_PhD_Project/ASTMON_Output/UCM-colores_Moon_20170401_20180926_FilterX_ASTMON.csv',header=0,sep =';')
ASTMONF.set_index('Datetime_Format1', inplace = True)
ASTMONF['Colors'] = ASTMONF.DataQuality_Flag.map({0:'Poor data quality_Cloudy',1:'Good data quality_No moon_no clouds',2:'Good data quality_Moon_No clouds'})
ASTMONF['Colors'] = ASTMONF.Colors.astype('category')# Category: improve efficiency 
ASTMONF.index = pd.to_datetime(ASTMONF.index)#Key: top level function (mask data with Pandas). 
ASTMONF['Time'] = ASTMON.index
ASTMONF.info(memory_usage='deep')

SQM_LEF = pd.read_csv('/Users/joserobles/Desktop/python3/Samples/UCM_PhD_Project/SQM_LE_Output/SQM_LE_Moon_FilterX.csv',header=0,sep =';')
SQM_LEF.set_index('Datetime_Format1', inplace = True)
SQM_LEF['Colors'] = SQM_LEF.DataQuality_Flag.map({0:'Poor data quality_Cloudy',1:'Good data quality_No moon_no clouds',2:'Good data quality_Moon_No clouds'})
SQM_LEF['Colors'] = SQM_LEF.Colors.astype('category')
SQM_LEF.index = pd.to_datetime(SQM_LEF.index)
SQM_LEF['Time'] = SQM_LEF.index
SQM_LEF.info(memory_usage='deep')

SQM_LUF = pd.read_csv('/Users/joserobles/Desktop/python3/Samples/UCM_PhD_Project/SQM_LU_Output/SQM_LU_Moon_FilterX.csv',header=0,sep =';')
SQM_LUF.set_index('Datetime_Format1', inplace = True)
SQM_LUF['Colors'] = SQM_LUF.DataQuality_Flag.map({0:'Poor data quality_Cloudy',1:'Good data quality_No moon_no clouds',2:'Good data quality_Moon_No clouds'})
SQM_LUF['Colors'] = SQM_LUF.Colors.astype('category')
SQM_LUF.index = pd.to_datetime(SQM_LUF.index)
SQM_LUF['Time'] = SQM_LUF.index
SQM_LUF.info(memory_usage='deep')

TESSF = pd.read_csv('/Users/joserobles/Desktop/python3/Samples/UCM_PhD_Project/TESS_W_Output/TESS_Moon_FilterX.csv',header=0,sep =';')
TESSF.set_index('Datetime_Format1', inplace = True)
TESSF['Colors'] = TESSF.DataQuality_Flag.map({0:'Poor data quality_Cloudy',1:'Good data quality_No moon_no clouds',2:'Good data quality_Moon_No clouds'})
TESSF['Colors'] = TESSF.Colors.astype('category')
TESSF.index = pd.to_datetime(TESSF.index)
TESSF['Time'] = TESSF.index
TESSF.info(memory_usage='deep')

#10.x.1] ASTMON-F: TIME LIMIT WITH PANDAS FLAVOUR
startF = pd.to_datetime('2017-04-01 15:00:00')
endF = pd.to_datetime('2017-04-02 05:00:00')
dif = pd.to_datetime('2017-04-02 15:00:00')
delta = dif-startF

#10.x.2] SQMLE-F
startSQMLEF = pd.to_datetime('2017-04-01 15:00:00')
endSQMLEF = pd.to_datetime('2017-04-02 06:00:00')

#10.x.3] SQMLU-F
startSQMLUF = pd.to_datetime('2017-04-01 15:00:00')
endSQMLUF = pd.to_datetime('2017-04-02 06:00:00')

#10.x.4] TESS-F
startTESS = pd.to_datetime('2017-04-01 15:00:00')
endTESS = pd.to_datetime('2017-04-02 06:00:00')

#10.1] ASTMON-F's MASK
for i in range(DAYS):
    print(startF,endF)
    startF = startF + delta
    endF = endF + delta
    ASTMONF[(ASTMONF.Time >= startF) & (ASTMONF.Time < endF)]# Passing boolings to data frame 
    maskF = ASTMONF[(ASTMONF.Time >= startF) & (ASTMONF.Time < endF)]
    print((ASTMONF.Time >= startF) & (ASTMONF.Time < endF))

#10.2] SQM-LEF's MASK
for i in range(DAYS):
    print(startSQMLEF,endSQMLEF)
    startSQMLEF = startSQMLEF + delta
    endSQMLEF = endSQMLEF + delta
    SQM_LEF[(SQM_LEF.Time >= startSQMLEF) & (SQM_LEF.Time < endSQMLEF)]# Passing boolings to data frame 
    maskSQMLE = SQM_LEF[(SQM_LEF.Time >= startSQMLEF) & (SQM_LEF.Time < endSQMLEF)]
    print((SQM_LEF.Time >= startSQMLEF) & (SQM_LEF.Time < endSQMLEF))

#10.3] SQM-LUF's MASK
for i in range(DAYS):
    print(startSQMLUF,endSQMLUF)
    startSQMLUF = startSQMLUF + delta
    endSQMLUF = endSQMLUF + delta
    SQM_LUF[(SQM_LUF.Time >= startSQMLUF) & (SQM_LUF.Time < endSQMLUF)]# Passing boolings to data frame 
    maskSQMLU = SQM_LUF[(SQM_LUF.Time >= startSQMLUF) & (SQM_LUF.Time < endSQMLUF)]
    print((SQM_LUF.Time >= startSQMLUF) & (SQM_LUF.Time < endSQMLUF))

#10.4] ASTMON-F's MASK
for l in range(DAYS):
    print(startTESS,endTESS)
    startTESS = startTESS + delta
    endTESS = endTESS + delta
    TESSF[(TESSF.Time >= startTESS) & (TESSF.Time < endTESS)]# Passing boolings to data frame 
    maskTESS = TESSF[(TESSF.Time >= startTESS) & (TESSF.Time < endTESS)]
    print((TESSF.Time >= startTESS) & (TESSF.Time < endTESS))


# APPARATUSES' PLOTS: MOON AND CLOUDS
for key, group in maskF.groupby(['Filter_codes','DataQuality_Flag','Colors'],as_index=True,axis=0).Magnitudes:# Create a Pandas series within groupby 
    key_clean = key[0].strip() 
    key_clean2 = key[1]
    key_clean3=key[2]
    plt.legend([startF.year],loc='best',fancybox=True,framealpha=0.3)
    plt.title('Magnitudes vs Time', color='black')
    plt.ylabel('Magnitudes(mag/arcsec^2)')
    group.plot(y='Magnitudes',style ='o',rot=0,c=first[key_clean],markersize=second[key_clean2],mfc=third[key_clean3],alpha=0.9,subplots=True,figsize=(12,8))
    maskSQMLE.Mag.plot(style='o',c='black',markersize=0.5,figsize=(12,8))
    maskSQMLU.Mag.plot(style='o',c='grey',markersize=0.5,figsize=(12,8))
    maskTESS.Mag.plot(style='o',c='m',markersize=0.5,figsize=(12,8))
    #plt.legend(('0_Clouds','SQM-LE','SQM-LU','TESS-W','1_No Moon no Clouds','2_Moon_no Clouds','0_Clouds','1_No Moon no Clouds','2_Moon_no Clouds','0_Clouds','1_No Moon no Clouds','2_Moon_no Clouds'),loc='best',fancybox=True,framealpha=0.3)
    print(key)
plt.tight_layout()    
plt.show()

'''
=======================
11] ASTMON's FilterX
=======================
''' 
#11.1] ASTROPY TIME FORMAT (ASTMON)
'''t = Time(ASTMON.Julian_Dates,format='jd',scale='utc')

#11.2] MOON AND ALTAZ 
altaz_moon = UCM.moon_altaz(t)# Needs format and scale!
ASTMON['AZ'] = altaz_moon.az
ASTMON['ALT'] = altaz_moon.alt

#11.3] Moon: Percent of Full and Phase 
Ilu = UCM.moon_illumination(t)
phase = UCM.moon_phase(t)
ASTMON['Percent of full'] = Ilu*100
ASTMON['Phase_angle'] = phase*(180/np.pi) 
ASTMON = ASTMON.assign(DataQuality_Flag = [2 if ALT > 0 else 1 for ALT in ASTMON['ALT']])
ASTMON = ASTMON.round({'Percent of full': 2,'Phase_angle':2,'AZ':2,'ALT':2})
ASTMON.to_csv('/Users/joserobles/Desktop/UCM-colores_Moon_20170401_20180926_FilterX.csv',index=True, header=True,sep =';')'''
#ASTMON.to_csv('/Users/joserobles/Desktop/UCM-colores_Moon_20170401_20180926_FilterX_Encoding_ascii.csv',index=True, header=True,sep =';',encoding='ascii')

'''
=======================
12] SQM-LE FilterX
=======================
'''
#12.1] MOON AND ALTAZ
'''SQM_LE['Julian_Dates']= SQM_LE.index.to_julian_date().astype('float')
tSQMLE = Time(SQM_LE.Julian_Dates,format ='jd',scale='utc')

altaz_moonSQMLE = UCM.moon_altaz(tSQMLE)
SQM_LE['AZ'] = altaz_moonSQMLE.az
SQM_LE['ALT'] = altaz_moonSQMLE.alt

Ilu_SQMLE = UCM.moon_illumination(tSQMLE)
phase_SQMLE = UCM.moon_phase(tSQMLE)
SQM_LE['Percent_of_full'] = Ilu_SQMLE*100
SQM_LE['Phase_angle[degrees]'] = phase_SQMLE*(180/np.pi) 
SQM_LE = SQM_LE.assign(DataQuality_Flag = [2 if ALT > 0 else 1 for ALT in SQM_LE['ALT']])
SQM_LE = SQM_LE.round({'Mag': 2,'Percent_of_full': 2,'Phase_angle[degrees]':2,'AZ':2,'ALT':2})
SQM_LE.to_csv('/Users/joserobles/Desktop/SQM_LE.csv',index=True,header=True,sep =';')'''

'''
=======================
13] SQM-LU FilterX
=======================
'''
'''SQM_LU['Julian_Dates']= SQM_LU.index.to_julian_date().astype('float')
tSQMLU = Time(SQM_LU.Julian_Dates,format ='jd',scale='utc')

altaz_moonSQMLU = UCM.moon_altaz(tSQMLU)
SQM_LU['AZ'] = altaz_moonSQMLU.az
SQM_LU['ALT'] = altaz_moonSQMLU.alt

Ilu_SQMLU = UCM.moon_illumination(tSQMLU)
phase_SQMLU = UCM.moon_phase(tSQMLU)
SQM_LU['Percent_of_full'] = Ilu_SQMLU*100
SQM_LU['Phase_angle[degrees]'] = phase_SQMLU*(180/np.pi) 
SQM_LU = SQM_LU.assign(DataQuality_Flag = [2 if ALT > 0 else 1 for ALT in SQM_LU['ALT']])
SQM_LU = SQM_LU.round({'Mag': 2,'Percent_of_full': 2,'Phase_angle[degrees]':2,'AZ':2,'ALT':2})
SQM_LU.to_csv('/Users/joserobles/Desktop/SQM_LU_Moon.csv',index=True,header=True,sep =';')'''

'''
=======================
14] SQM-LU FilterX
=======================
'''
'''TESS['Julian_Dates']= TESS.index.to_julian_date().astype('float')
tTESS = Time(TESS.Julian_Dates,format ='jd',scale='utc')

altaz_moonTESS = UCM.moon_altaz(tTESS)
TESS['AZ'] = altaz_moonTESS.az
TESS['ALT'] = altaz_moonTESS.alt

Ilu_TESS = UCM.moon_illumination(tTESS)
phase_TESS = UCM.moon_phase(tTESS)
TESS['Percent_of_full'] = Ilu_TESS*100
TESS['Phase_angle[degrees]'] = phase_TESS*(180/np.pi)
TESS = TESS.assign(DataQuality_Flag = [2 if ALT > 0 else 1 for ALT in TESS['ALT']])
TESS = TESS.round({'Mag': 2,'Percent_of_full': 2,'Phase_angle[degrees]':2,'AZ':2,'ALT':2})
TESS.to_csv('/Users/joserobles/Desktop/TESS_Moon_FilterX.csv',index=True,header=True,sep =';')'''



#FOR LARGE FILES: CHUCNK THE DATA (SEE THE PROCEDURE FOR SQM_LE BELLOW) 
'''chunks = 10000
SQM_LE_cols_names = ['Datetime_Format1','Datetime_F2_LE','Temp_sensor','D','Freq','Mag']

G = []
for SQM_LE in pd.read_csv('/Users/joserobles/PhD_UCM_Astrophysics/DriveZamorano/Datos_originales/SQM/SQM_LE/data_UCM-SQM-LE-1952_2017_2018.csv',iterator=True,chunksize=chunks,header = None,sep =';',names=SQM_LE_cols_names):
    SQM_LE.drop(['Temp_sensor','D','Freq','Datetime_F2_LE'],axis=1,inplace=True)
    #4.1.2] Cleaning Process
    SQM_LE.Mag >= 14 #14
    SQM_LE = SQM_LE[SQM_LE.Mag >= 14]# Cut-off: 14 mag/arsec^2
    SQM_LE.Mag <= 19 #18
    SQM_LE = SQM_LE[SQM_LE.Mag <= 19]
    SQM_LE['Datetime_Format1'] = pd.to_datetime(SQM_LE['Datetime_Format1'],utc=True)
    SQM_LE.set_index('Datetime_Format1',inplace=True)
    SQM_LE['DataQuality_Flag'] = 1
    SQM_LE['Julian_Dates']= SQM_LE.index.to_julian_date()
    SQM_LE.dropna(how='any')
    tSQMLE = Time(SQM_LE.Julian_Dates,format ='jd',scale='utc')
    altaz_moonSQMLE = UCM.moon_altaz(tSQMLE)
    SQM_LE['AZ'] = altaz_moonSQMLE.az
    SQM_LE['ALT'] = altaz_moonSQMLE.alt
    Ilu_SQMLE = UCM.moon_illumination(tSQMLE)
    phase_SQMLE = UCM.moon_phase(tSQMLE)
    SQM_LE['Percent_of_full'] = Ilu_SQMLE*100
    SQM_LE['Phase_angle[degrees]'] = phase_SQMLE*(180/np.pi) 
    SQM_LE = SQM_LE.assign(DataQuality_Flag = [2 if ALT > 0 else 1 for ALT in SQM_LE['ALT']])
    SQM_LE = SQM_LE.round({'Percent_of_full': 2,'Phase_angle[degrees]':2,'AZ':2,'ALT':2})
    SQM_LE.info(memory_usage='deep')
    G.append(SQM_LE)
    df = pd.concat(G, ignore_index=False)
    df.to_csv('/Users/joserobles/Desktop/SQM_LE_TEST_Chunks.csv',index=True,header=True,sep =';')'''