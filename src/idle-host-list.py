#!/usr/bin/env python
# coding: utf-8

# In[27]:


import pandas as pd


# In[31]:


def virtual_machine_location():
    data = {'Id':range(1,11),'Name': ['VM_Master', 'VM_Worker1', 'VM_Worker2', 'VM_Worker3', 'VM_Worker4', 
                                      'VM_Worker5','VM_Worker6', 'VM_Worker7', 'VM_Worker8', 'VM_Worker9'], 
            "IP" : ['http://10.4.41.64:9870', 'http://10.4.41.54:9870', 'http://10.4.41.49:9870', 
                   'http://10.4.41.59:9870', 'http://10.4.41.63:9870', 'http://10.4.41.68:9870', 
                   'http://10.4.41.69:9870', 'http://10.4.41.72:9870', 'http://10.4.41.74:9870',
                   'http://10.4.41.76:9870'],
            'User': 'bdm', 'Password' : 'asY76fkG12'}    
    df = pd.DataFrame(data)  
    df.to_csv('/home/vladka/Downloads/BDMA/idle-host-list.csv',index=False)
    return("Ok")


# In[32]:


virtual_machine_location()

