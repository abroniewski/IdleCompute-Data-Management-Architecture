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
import pandas as pd
from pyspark.sql.functions import udf
from pyspark.rdd import portable_hash

appName = "Scala Parquet Example"
master = "local"

spark = SparkSession.builder.appName(appName).master(master).getOrCreate()

#%%
import os

cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
files = os.listdir(cwd)
print("Files in %r: %s" % (cwd, files))
#%% load
#TODO: iterate through folder structure to find file
#TODO: Looks like python is not using the /src directory as current working directory??
ip = [37, 38, 39]
workload = [20, 30, 50]

data_location = 'data/processed/2022/03/VKY001-001-AB12'
schedule = pd.read_csv('data/admin/idle-host-schedule-2022-05-25-17-34.csv') #TODO: why not ../data???


#%%
##########################
#     Parquet read and partition
##########################
# Read Parquet file
dataset_rdd = spark.read.parquet(data_location).rdd
row_count = dataset_rdd.count()

number_of_rows1 = int(0.2*row_count)  # splitting number of rows for each subset
number_of_rows2 = int(0.3*row_count)
number_of_rows3 = int(0.5*row_count)

# determining boundaries for each section of work
second_lower = int(number_of_rows1)
third_lower = second_lower + int(number_of_rows2)

dataset_rdd2 = dataset_rdd.zipWithIndex()  # adding index to dataframe
dataset_rdd3 = dataset_rdd2.map(lambda x: (x[1], x[0]))  # creating key value pair
dataset_rdd4 = dataset_rdd3.map(lambda x: ((1 if x[0] < second_lower else (2 if x[0] < third_lower else 3)), x[1]))

column_names = ["key", "value"]
dataset_df = dataset_rdd4.toDF(column_names)
dataset_df.printSchema()

#%%
dataset_df.write.option("header",True) \
        .partitionBy("key") \
        .mode("overwrite") \
        .parquet("data/tmp/test_output_parquet")

#%%
print("done")
spark.stop()

