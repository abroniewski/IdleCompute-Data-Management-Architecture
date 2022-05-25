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

appName = "Scala Parquet Example"
master = "local"

spark = SparkSession.builder.appName(appName).master(master).getOrCreate()

#%% load
#TODO: iterate through folder structure to find file
ip = [[37, 38, 39]]
workload = [[20, 30, 50]]

data_location = '../data/processed/2022/03/VKY001-001-AB12'
schedule = pd.read_csv('../data/admin/schedule.csv')


dataset = spark.read.parquet(data_location)

# ip_assignment = workload[0][0]

# rdd1 = spark.sparkContext.parallelize(dataset)
# rdd2 = dataset.rdd.map(lambda x: )

#%%
# df1=dataset.rdd.zipWithIndex().toDF()
# df2=df1.select(cols("_1.*"),cols("_2").alias('increasing_id'))
# df1.show(1)
# print("done")
#%%
nums = list(range(0,1000001))
print(len(nums))
nums_rdd = spark.sparkContext.parallelize(nums)
squared_nums = nums_rdd.map(lambda x: x ** 2)
print(nums_rdd)
rdd_index = squared_nums.zipWithIndex()
rdd_index.take(5)

#%%
##########################
###     Example of Key + MapReduce by Workload
##########################
# row_count = dataset.count()
nums = list(range(1,100))  # create dummy test set
row_count = len(nums)  # save length of test set
nums_rdd = spark.sparkContext.parallelize(nums)  #create RDD

number_of_rows1 = 0.2*row_count  # splitting number of rows for each subset
number_of_rows2 = 0.3*row_count
number_of_rows3 = 0.5*row_count

first_lower = 0  #determinging upper/loser boundaries for each section of work
first_upper= first_lower + int(number_of_rows1) - 1
second_lower = first_upper + 1
second_upper = second_lower + int(number_of_rows2) - 1
third_lower = second_upper + 1
third_upper = row_count-1
print(row_count)
print ([first_lower,first_upper],[second_lower,second_upper],[third_lower,third_upper])

nums2 = nums_rdd.zipWithIndex()  # adding index to dataframe
nums3 = nums2.map(lambda x: (x[1],x[0] ** 2))  # creating some visual difference between values and hey
# TODO: There is a flaw in this logic, as only 1 and 2 are assigned to each row
nums4 = nums3.map(lambda x: ((1 if x[0] < second_lower else (2 if (x[0] >= second_lower && x[0] < third_lower) else (3
if x[0] >= third_lower else 4))),x[0],x[1]))  # logic to assign key.
nums4.collect()  # show results
# getPartition()  # will be called to send each row to different partition based on its key.

#%%
dataset_index = dataset.rdd.zipWithIndex()  # transform spark.DataFrame into RDD and add sequential index
dataset_index2 = dataset_index.map(lambda x: (x[1],x[0]))  # flip the index and value to behave as key/value pair
# dataset_index3 = dataset_index2.map(lambda x: (1 if x[1],x[0]))

# map(lambda x: 'lower' if x < 3 else 'higher', lst)

#%%
print("done")
spark.stop()

