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

import pandas as pd
import re


#TODO: iterate through folder structure to find file
def retrieve_IP_and_partition_size(data_location):
        ip = [37, 38, 39]
        workload_distribution = [20, 30, 50]

        return ip, workload_distribution


# ip, workload_distribution = retrieve_IP_and_partition_size(data_location)
def partition_output_directory(partitioned_directory, file_location):
        metadata = re.split('[/]', file_location)  # splits the filename on '/' -> creates a list
        file_directory = f"{partitioned_directory}/{metadata[2]}/{metadata[3]}/{metadata[4]}"  # uses YYYY/MM subdirectory name
        return file_directory


##########################
#     Parquet read and partition
##########################
# Read Parquet file
def read_parquet_dataset_for_partition(spark_session, data_location):
    # df = spark_session.read.csv(path=data_location, schema=schema, header=True)
    df = spark_session.read.parquet(data_location)
    # dataset_rdd2 = dataset_rdd.map(lambda x: (x[1]))
    # df = dataset_rdd2.map(lambda x: (x,)).toDF()
    # df = dataset_rdd2.toDF()
    df.show()
    print(f"Parquet data loaded from {data_location}")
    return df


def read_csv_dataset_for_partition(spark_session, data_location, schema):
    df = spark_session.read.csv(path=data_location, schema=schema, header=True)
    print(f"CSV data loaded from {data_location}")
    return df


# TODO: iterate through ip and workload
def partition_scheduled_dataset(dataset_rdd, idlehost_ip, workload, output_directory):
        # dataset_rdd = spark.read.parquet(file_location).rdd
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
        dataset_rdd4 = dataset_rdd3.map(
                lambda x: ((37 if x[0] < second_lower else
                            (38 if x[0] < third_lower else 39)), x[1]))

        column_names = ["key", "value"]
        dataset_df = dataset_rdd4.toDF(column_names)

        # output_location = partition_output_directory(partitioned_directory=output_directory,
        #                                              file_location=file_location)

        dataset_df.write.option("header",True) \
                .partitionBy("key") \
                .mode("overwrite") \
                .parquet(output_directory)


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
