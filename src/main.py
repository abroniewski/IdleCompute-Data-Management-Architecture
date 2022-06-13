# from idle_host_list import *
from partition_dataset import *
from dataset_analytics import *


DATA_DIRECTORY = "../data/processed/"
FORMATTED_DIRECTORY = "../data/partitioned"
ANALYZED_DIRECTORY = "../data/analyzed"
current_analytics_dataset = "2022/03/VKY001-002-AB12"


TEMPORAL_DIR = '../data/raw'
CONVERTED_DIR = '../data/processedTemp'
HDFS_DIR = DATA_DIRECTORY

DATA_LOCATION = "../data/raw/2022-06-05-UCIHD-001-AB12.csv"
analytics_save_location = "../data/analyzed/2022/06/UCIHD-001-AB12"

spark = start_spark()

# cluster_slave_ip, workload_distribution = retrieve_IP_and_partition_size(
#     data_location=DATA_DIRECTORY)

next_file = os.path.join(DATA_DIRECTORY, "2022/06")
data_rdd = read_parquet_dataset_for_partition(
    spark_session=spark,
    data_location=next_file).rdd

schema = define_dataset_schema(
    data_location=DATA_DIRECTORY,
    dataset=current_analytics_dataset,
    data_type=None)

# data_rdd = read_csv_dataset_for_partition(
#     spark_session=spark,
#     data_location=os.path.join(next_file, "UCIHD-001-AB12.csv"),
#     schema=schema).rdd

output_file = os.path.join(FORMATTED_DIRECTORY, "2022/06")
partition_scheduled_dataset(
    dataset_rdd=data_rdd,
    idlehost_ip=None,
    workload=None,
    output_directory=output_file)

### This code would be used if we are running everything from VM cluster
# data_location = 'data/processed/2022/03/VKY001-002-AB12'
# current_location = partition_output_directory(
#     partitioned_directory="data/partitioned",
#     file_location=data_location)
# move_partitions_to_hdfs(
#     HDFS_directory="data/partitioned",
#     current_file_location=data_location)


### ANALYTICS

columns = import_dataset_headers(
    data_location=DATA_LOCATION)

# df = read_dataset_for_analysis(
#     spark_session = spark,
#     data_location=DATA_LOCATION,
#     schema=schema)

df = read_parquet_dataset_for_analysis(
    spark_session=spark,
    data_location=output_file)

generate_descriptive_analytics_files(
    columns=columns,
    analysis_dataframe=df,
    analytics_save_location=analytics_save_location)

train_data, test_data, feature_column = transform_data_to_target_schema(
    columns=columns,
    analysis_dataframe=df)

linearModel = integrate_parameters_and_build_LR_model(
    parameter_location="../data/test-data/parameters.csv",
    training_data=train_data,
    analytics_save_location=analytics_save_location)

validate_LR_model(
    LR_model=linearModel,
    testing_data=test_data,
    analytics_save_location=analytics_save_location)

stop_spark(
    spark_session=spark)