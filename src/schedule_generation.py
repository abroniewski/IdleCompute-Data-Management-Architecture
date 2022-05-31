import pandas as pd

# Create IdleHost schedule file (ADAM)
#   INPUT: None
#   OUTPUT: 3 static CSV files -> "idle-host-schedule-YYYY-MM-DD-HH-MM.csv"
#   SCOPE:
#       Define Scheduling Inputs that get used to assign dataset + job to the correct workerNodes based on
#       availability. These will be pre-generated CSV files that would be created by group2 scheduling work. They act
#       as an input for the analysis process. We will create several of these files ahead of time and have a script
#       that makes them available as a process inout for the MVP.
#       Data to include:
#           YYYY, MM, DD, UserID, TaskId, AnalysisType, IdleHostIP, %workLoad


def create_dummy_schedule():
    # TODO: remove hard-coding of this schedule generation
    # idlehost ip is the las digits of the IP address of the hose (this lines up with the VM IP address, but can be
    #   treated as a unique ID for now.
    # workload is a percentage of workload that each IP will handle
    # expected output for a dataset of 5 rows that are split 40% to IP 37 and 60% to IP 39
    #   |  key  |   -value-                 |
    #   |   37  |   -original dataset row-  |
    #   |   37  |   -original dataset row-  |
    #   |   39  |   -original dataset row-  |
    #   |   39  |   -original dataset row-  |
    #   |   39  |   -original dataset row-  |
    yyyy = [2019, 2020, 2021, 2022]  # year directory where unprocessed data exists
    mm = [[7], [12], [2, 4], [3]]  # month directory
    user_id = [["ABR001"], ["ABR001"], ["ABR001", "VKY001"], ["ABR001", "VKY001", "VKY001", "VKY001"]]
    task_id = [[2], [2], [5, 1], [2, 1, 2, 3]]
    analysis_type = [["AB12"], ["AB12"], ["AB12", "AB12"], ["AB12", "AB12", "AB12", "AB12"]]
    idlehost_ip = [[["10.4.41.64", "10.4.41.38", "10.4.41.39"]], [["10.4.41.37", "10.4.41.39"]], [["10.4.41.37", "10.4.41.38", "10.4.41.40"], ["10.4.41.37", "10.4.41.38", "10.4.41.39"]], [["10.4.41.38", "10.4.41.39"], ["10.4.41.39"], ["10.4.41.37", "10.4.41.39"], ["10.4.41.37",
                                                                                                                 40, 39]]]
    workload = [[[20, 30, 50]], [[50, 50]], [[10, 5, 85], [35, 35, 30]], [[10, 90], [100], [40, 60], [34, 33, 33]]]

    dataset = {"yyyy": yyyy, "mm": mm, "user_id": user_id, "task_id": task_id,
               "analysis_type": analysis_type,
               "idlehost_ip": idlehost_ip,
               "workload": workload}

    schedule = pd.DataFrame(data=dataset)
    print(schedule.columns)
    pd.DataFrame(data=dataset).to_csv('../data/admin/schedule.csv', index=False)


create_dummy_schedule()