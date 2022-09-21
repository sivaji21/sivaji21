# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 10:59:18 2022

@author: s344542
"""

#%%
import os

result=[]

files = [file for file in os.listdir(".") if (file.lower().endswith('.csv'))]
files.sort(key=os.path.getmtime)
for file in sorted(files,key=os.path.getmtime):
    result.append(file)
  
# print(result)
blu_4 = result[0]
blu_4_tm = result[1]
blu_7 = result[2]
blu_7_tm = result[3]
print(blu_4,blu_4_tm,blu_7,blu_7_tm)

#%%
"""
plot blutooth & create an offset (not done yet code in monthly presentation)
"""
import pandas  as pd
import matplotlib.pyplot as plt# 
import numpy as np

ang4 = np.loadtxt(blu_4,delimiter=',', skiprows=1)
ang4_tm = np.loadtxt(blu_4_tm,delimiter=',', skiprows=1)
ang7 = np.loadtxt(blu_7,delimiter=',', skiprows=1)
ang7_tm = np.loadtxt(blu_7_tm,delimiter=',', skiprows=1)
t4 = ang4_tm[:]
s=len(t4)
X4 = ang4[0:s, 0]
Y4 = ang4[0:s, 1]
Z4 = ang4[0:s, 2]
t7 = ang7_tm[:]
f=len(t7)
X7 = ang7[0:f, 0]
Y7 = ang7[0:f, 1]
Z7 = ang7[0:f, 2]


#%%
# plt.plot(t4, Y4, '-', label='Angle from Inclinometer')
# plt.plot(t4, X4, '-', label='Angle from Inclinometer')
# plt.plot(t4, Z4, '-', label='Angle from Inclinometer')
# plt.plot(t7, Y7, '-', label='Angle from Inclinometer')
# plt.plot(t7, X7, '-', label='Angle from Inclinometer')
# plt.plot(t7, Z7, '-', label='Angle from Inclinometer')

plt.figure()
plt.plot(t4, Z4, '-', label='Z Angle from Inclinometer')
plt.plot(t4, X4, '-', label='X Angle from Inclinometer')
plt.plot(t4, Y4, '-', label='Y Angle from Inclinometer')
# plt.plot(t, j2,'.', label= 'Angle from Robot')
# plt.plot(t_r, ang2, label= 'Angle from RRI phase measured')
plt.title("Comparison Joint Angles ")
plt.xlabel("Time in seconds")
plt.ylabel(" Angle in degrees")
plt.rcParams['figure.figsize'] = [8.27, 11.69]
plt.rcParams['figure.dpi'] = 140
plt.legend(loc='best')
plt.show()
plt.savefig('Comparison_4.png')

#%%
plt.figure()
plt.plot(t7, Z7, '-', label='Z Angle from Inclinometer')
plt.plot(t7, X7, '-', label='X Angle from Inclinometer')
plt.plot(t7, Y7, '-', label='Y Angle from Inclinometer')
# plt.plot(t, j2,'.', label= 'Angle from Robot')
# plt.plot(t_r, ang2, label= 'Angle from RRI phase measured')
plt.title("Comparison Joint Angles ")
plt.xlabel("Time in seconds")
plt.ylabel(" Angle in degrees")
plt.rcParams['figure.figsize'] = [8.27, 11.69]
plt.rcParams['figure.dpi'] = 140
plt.legend(loc='best')
plt.show()
plt.savefig('Comparison_7.png')

