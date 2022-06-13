from partition_dataset import *
from dataset_analytics import *
from machine_in_progress import *
from landing_zone import *

# persistent locations and global data directories
DATA_DIRECTORY = "../data/processed/"  # this is the landing zone from P1
FORMATTED_DIRECTORY = "../data/partitioned"  # formatted zone
ANALYZED_DIRECTORY = "../data/analyzed"  # location of analytics and modelling outputs
ADMIN_DIRECTORY = "../data/admin"  # directory with admin files generated by other team
TEMPORAL_DIR = '../data/raw'  # temporal landing zone from P1

create_persistent_local_directory(persistent_landing_dir=PERSISTENT_ZONE_DIR, temporal_landing_dir=TEMPORAL_ZONE_DIR)

spark = start_spark()

# iterating through schedule CSV to retrieve the next scheduled dataset to be completed
next_file = machine_in_progress_list(ADMIN_DIRECTORY)  # finds the file
next_file_dir = os.path.join(DATA_DIRECTORY, next_file)  # creates the directory of the dataset
analytics_save_location = os.path.join(ANALYZED_DIRECTORY, next_file)  # creating directory for output files

# read dataset (parquet) in as RDD file to be landed in formatted zone
data_rdd = read_parquet_dataset_for_partition(
    spark_session=spark,
    data_location=next_file_dir).rdd

# retrieving the schema for the scheduled dataset (schema is saved during upload)
schema = define_dataset_schema(
    data_location=DATA_DIRECTORY,
    dataset=next_file_dir,
    data_type=None)

# generating and outputting a partitioned file based on input workloads
# dataset is written to partitioned directory
output_file = os.path.join(FORMATTED_DIRECTORY, "2022/06/UCIHD-001-AB12")
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
# reading in the column names from a metadata file (provided by user)
columns = import_dataset_headers(
    data_location="../data/raw/2022-06-05-UCIHD-001-AB12.csv")

# read parquet file from partitioned dataset stored in FORMATTED directory
df = read_parquet_dataset_for_analysis(
    spark_session=spark,
    data_location=output_file)

# generate analytics visualizations
# visualizations are written to analytics directory in PNG and PICKLE format
generate_descriptive_analytics_files(
    columns=columns,
    analysis_dataframe=df,
    analytics_save_location=analytics_save_location)

# creating exploitation view
train_data, test_data, feature_column = transform_data_to_target_schema(
    columns=columns,
    analysis_dataframe=df)

# building LR model
# This code (and some data processing above) would be wrapped in conditional statements
# depending on the type of analytics that are requested by the user
# model is written to analyzed directory
linearModel = integrate_parameters_and_build_LR_model(
    parameter_location="../data/test-data/parameters.csv",
    training_data=train_data,
    analytics_save_location=analytics_save_location)

# generating model validation metrics
# metrics are output in CSV file to analyzed directory
validate_LR_model(
    LR_model=linearModel,
    testing_data=test_data,
    analytics_save_location=analytics_save_location)

stop_spark(
    spark_session=spark)