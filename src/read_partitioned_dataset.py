from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.functions import udf
from pyspark.rdd import portable_hash

import pandas as pd
import re

appName = "Scala Parquet Example"
master = "local"

spark = SparkSession.builder.appName(appName).master(master).getOrCreate()

data_location = 'data/partitioned/2022/03/VKY001-002-AB12'

##########################
#     Parquet read and partition
##########################
# Read Parquet file
def read_partitioned_dataset(file_location, idlehost_ip, workload):
        dataset_rdd = spark.read.parquet(file_location).rdd

read_partitioned_dataset(file_location=data_location, idlehost_ip=None, workload=None)
print("done partition_scheduled_dataset")

spark.stop()
print("spark session ended")

