'''
====================================================================================================================
Lesson1: Structure and Cleaning Process of a Data Frame
Objective: to understand the process of structuring and cleaning a data frame. 

Tasks: 
       1_To read an .csv files
       2_To learn how to structucture a data frame
       3_To start a cleanning process 
====================================================================================================================
'''
'''
=======================
1] LIBRARIES
=======================
''' 
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
matplotlib.style.use('ggplot')

'''
=======================
2] ASTMON DATA FRAME, CLEANING PROCESS, AND COLOR INDEX
=======================
''' 
#2.1] ASTMON'S DATA FRAME
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

#2.2] CLEANING PROCESS
ASTMON.dropna(how='any')
ASTMON.set_index('Datetime_Format1', inplace = True)
ASTMON['Filter_codesNumber']=ASTMON['Filter_codes'].cat.codes# pulling out codes behind Filter_codes
ASTMON.info(memory_usage='deep')
print(ASTMON.describe())
print(ASTMON)
