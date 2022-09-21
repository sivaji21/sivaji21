# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 09:59:08 2022
combined script to take readings , convert them to angle from rri ,
creating an offset to start reading from 0.
@author: s344542
"""
"""
imports
"""


import time
import numpy  as np
from datetime import datetime
import bt901n
import pandas as pd


#%%
"""
setup arm
"""
bt4 = bt901n.BT901('com4')
bt7 = bt901n.BT901('com7')
bt4.start_logging()
bt7.start_logging()


#%% 
"""
Measurement

"""

bt4.enable_time(True)
bt7.enable_time(True) #needs 2nd run to enable?
bt4.reset_data()
bt7.reset_data()

time.sleep(.01)
#Start arm program



#records data for the set time
time.sleep(450)

#stops recording data

# bt4.stop_logging() #worked when it is not in the script
# bt7.stop_logging()

#get the data recorded 
t4,a,g,ang4,mag = bt4.get_data()
t7,a,g,ang7,mag = bt7.get_data()
bt4_time =t4 
bt7_time =t7
del a,g,mag #not needed



#%%
"""
save data recorded
1.bluettoh
"""

time_start4 = t4[0] # first reading of time
tim4_c = t4-time_start4 # subtracr first reading from all other time readings to start from 0
time_start7 = t7[0] # first reading of time
time7_c = t7-time_start7 # subtracr first reading from all other time readings to start from 0
fl = datetime.now().strftime("%d_%m_%H_%M_%S") # current time to name files
s  = pd.DataFrame(ang4)
ang4_ad=s - s.iloc[0]
s1  = pd.DataFrame(ang7)
ang7_ad=s1 - s1.iloc[0]
np.savetxt( './blu4_'+fl+'.csv', ang4_ad, delimiter=',',header="X,Y,Z", comments='')
np.savetxt( './blu4_tm'+fl+'.csv', tim4_c, delimiter=',',header="T", comments='')
np.savetxt( './blu7_'+fl+'.csv', ang7_ad, delimiter=',',header="X,Y,Z", comments='')
np.savetxt( './blu7_tm'+fl+'.csv', time7_c, delimiter=',',header="T", comments='')
np.savez('./ang_4'+fl+'.npz',ank=ang4_ad,t41=tim4_c)










#%%
import os
import shutil
from datetime import datetime



source = r'C:/Users/s344542/OneDrive - Cranfield University/code_written_by_day/19_09_22'
destination = datetime.now().strftime("%d_%m_%H_%M_%S")

def move(): # defining the statement move
    if not os.path.exists(source+datetime.now().strftime("%d_%m_%H_%M_%S")): #if folder called im is not present
      os.makedirs(datetime.now().strftime("%d_%m_%H_%M_%S")) #create a folder datetime
      for i in os.listdir(source): # list all files in source folder
          if i.endswith('.csv'): #if it is a .csv file
              shutil.move(os.path.join(source,i),destination) #move the file to destination
move()     


#%%
"""
close bt ports if necessary
"""
bt4.stop_logging()
bt7.stop_logging()
bt4.close()
bt7.close()

"""
offset reading to 0 (not done yet copy from montly meeting code)
create plots to visuliase the data received
plot robot 
"""