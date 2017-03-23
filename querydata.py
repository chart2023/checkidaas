#!/usr/bin/python
# coding: utf-8
import os
os.chdir('/home/ubuntu/bems_analytic')
# In[5]:

import ThesisFunction as Khetnon
Khetnon.MainLibary() #Load library
Khetnon.Create_AllPoint() #Load Point ID
from datetime import datetime
from datetime import timedelta
import pandas as pd


# In[6]:

# In[7]:

# In[8]:


# In[ ]:



# In[5]:

def Update_Wasted_energy(Time,Thres_User_disapper,Temp_thres,Mode="Update"):
    Scale = 'Build4'
    if Mode == 'Update':
        for t in range(1,Time+1):
            Khetnon.Main_Wasted_Energy_Calculation_ALL (Scale,t,Thres_User_disapper,Temp_thres,Check_Value='Yes',Write_Storage = 'Yes')
    elif Mode == 'ReWrite':
        for t in range(1,Time+1):
            Khetnon.Main_Wasted_Energy_Calculation_ALL (Scale,t,Thres_User_disapper,Temp_thres,Check_Value='No',Write_Storage = 'ReWrite')
    elif Mode == 'Test':
        for t in range(1,Time+1):
            Khetnon.Main_Wasted_Energy_Calculation_ALL (Scale,t,Thres_User_disapper,Temp_thres,Check_Value='No',Write_Storage = 'No')


# In[6]:

Update_Wasted_energy(Time=5,Thres_User_disapper=15,Temp_thres=24,Mode="Test")


# In[ ]:


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



