# Partition dataset or assign chunks based on schedule (ADAM)
#   INPUT:
#       pandas.dataframe -> current_job_schedule
#       analysis job dataset
#   OUTPUT:
#       pandas.dataframe -> current_job_schedule updated
#       EITHER updated dataset stored in /../data/processed/YYYY/MM/scheduled/IdleHostID
#       OR return the parameters/variables needed to distributed Hadoop chunks
#   SCOPE:
#       For all jobs that are not started, check to see if the required hosts (VMs) are available. If all VMs are
#       available:
#       EITHER add key to each row of data based on number of nodes that will be used. Store dataset in scheduled
#       OR see if we can set which location Hadoop sends its chunks to? Output would be a hadoop call/function
#       update scheduled current_job_schedule[status == "scheduled"]

# Note: The Name Node will replicate blocks to data nodes based upon rack configuration, replication factor and node
# availability, so even if you do managed to get a block on two particular data nodes, if one of those nodes goes
# down, the name node will replicate the block to another node. Your requirement is also assuming a replication
# factor of 1, which doesn't give you any data redundancy (which is a bad thing if you lose a data node). Let the
# namenode manage block assignments and use the balancer periodically if you want to keep your cluster evenly
# distributed

#%% import
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import udf
from pyspark.rdd import portable_hash

import pandas as pd
import re

appName = "Scala Parquet Example"
master = "local"

spark = SparkSession.builder.appName(appName).master(master).getOrCreate()

#%% load
#TODO: iterate through folder structure to find file
ip = [37, 38, 39]
workload_distribution = [20, 30, 50]

data_location = 'data/processed/2022/03/VKY001-002-AB12'

#%%
def partition_output_directory(partitioned_directory, file_location):
        metadata = re.split('[/]', file_location)  # splits the filename on '/' -> creates a list
        file_directory = f"{partitioned_directory}/{metadata[2]}/{metadata[3]}/{metadata[4]}"  # uses YYYY/MM subdirectory name
        return file_directory

#%%
##########################
#     Parquet read and partition
##########################
# Read Parquet file
def partition_scheduled_dataset(file_location, idlehost_ip, workload):
        print(file_location)
        dataset_rdd = spark.read.parquet(file_location).rdd
        row_count = dataset_rdd.count()

        # TODO: Iterate through workload and create boundaaries regardless of how many nodes we have
        number_of_rows1 = int(0.2*row_count)  # splitting number of rows for each subset
        number_of_rows2 = int(0.3*row_count)

        # determining boundaries for each section of work
        second_lower = int(number_of_rows1)
        third_lower = second_lower + int(number_of_rows2)

        # TODO: create partitions regardless of how many nodes are being used
        # adding index to dataframe and creating key value pair based on workload %
        dataset_rdd2 = dataset_rdd.zipWithIndex()
        dataset_rdd3 = dataset_rdd2.map(lambda x: (x[1], x[0]))
        dataset_rdd4 = dataset_rdd3.map(lambda x: ((37 if x[0] < second_lower else (38 if x[0] < third_lower else
                                                                                     39)),
                                                   x[1]))

        column_names = ["key", "value"]
        dataset_df = dataset_rdd4.toDF(column_names)

        output_location = partition_output_directory(partitioned_directory="data/partitioned",
                                                     file_location=file_location)

        dataset_df.write.option("header",True) \
                .partitionBy("key") \
                .mode("overwrite") \
                .parquet(output_location)

#%%
def get_IP_from_schedule(schedule: pd.DataFrame):
        """
        Get IP addresse from schedule CSV
        :return:
        """

def get_workload_from_schedule():
        """
        Get workload % from schedule corresponding to each IP address.
        :return:
        """

#%%
# TODO: create function that iterates and creates necessary directories (used in landing zone and here)
def move_partitions_to_hdfs(HDFS_directory, current_file_location):
        metadata = re.split('[/]', current_file_location)  # splits the current_file_location on '/' -> creates a list

        hdfs_existing_directory_year = client.list(HDFS_DIR, status=False)
        if metadata[2] not in hdfs_existing_directory_year:  # creates the directory if it doesn't exist. Check year
                client.makedirs(f"{HDFS_DIR}/{metadata[2]}/{metadata[3]}", permission=None)
        hdfs_existing_directory_month = client.list(f"{HDFS_DIR}/{metadata[2]}", status=False)
        if metadata[1] not in hdfs_existing_directory_month:  # check if month exists
                client.makedirs(f"{HDFS_DIR}/{metadata[2]}/{metadata[3]}", permission=None)

        HDFS_partitioned_file_location = f"{HDFS_directory}/{metadata[2]}/{metadata[3]}"
        client.upload(HDFS_partitioned_file_location, "../data/partitioned/2022/03/VKY001-002-AB12")


#%%
partition_scheduled_dataset(file_location=data_location, idlehost_ip=None, workload=None)

print("done partition_scheduled_dataset")

#%%
import re
from hdfs import InsecureClient

HDFS_DIR = './data/partitioned'
client = InsecureClient('http://10.4.41.82:9870', user='bdm')  # this IP should be changed to your personal VM
current_location = partition_output_directory(partitioned_directory="data/partitioned",
                                                     file_location=data_location)

client.makedirs(HDFS_DIR)
move_partitions_to_hdfs(HDFS_DIR, current_location)

#%%

spark.stop()
print("spark session ended")

