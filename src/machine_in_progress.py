#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd


# In[ ]:


def machine_in_progress_list():
    
    file_path = '../data/admin/'
    schedule = pd.read_csv(f"{file_path}schedule_new.csv")
    
    machine_in_progress = []
    task_in_progress_indexes = [n for n,x in enumerate(schedule['status']) if x=='in_progress']
    
    for k in task_in_progress_indexes:
        machines = schedule['idlehost_ip'][k].replace('[',' ').replace(']',' ').replace(',',' ').split()
        for t in machines:
            machine_in_progress.append(t)
            
    machine_in_progress = list(dict.fromkeys(machine_in_progress))
    df = pd.DataFrame(columns=['IP'])
    df['IP'] = machine_in_progress
    
    df.to_csv(f'{file_path}machine_in_progresse.csv', index=True)


# In[ ]:


machine_in_progress_list()

