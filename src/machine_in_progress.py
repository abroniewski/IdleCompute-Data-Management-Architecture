import pandas as pd
import os


def machine_in_progress_list(admin_file_directory):
    schedule = pd.read_csv(os.path.join(admin_file_directory, "schedule.csv"))
    next_machine = []
    for task in schedule.iterrows():
       if task[1]["status"]=="in_progress":
           next_machine = f"{task[1]['yyyy']}/{task[1]['mm']}/{task[1]['user_id']}-00{task[1]['task_id']}" \
                          f"-{task[1]['analysis_type']}"
    return next_machine


