import pandas as pd
import numpy as np

from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import LinearRegression
from pyspark.mllib.evaluation import MulticlassMetrics

import handyspark

import matplotlib.pyplot as plt
import pickle

# import pyspark.sql.functions as F
# from pyspark import SparkConf, SparkContext
# from pyspark.sql.functions import udf, col
# from pyspark.mllib.evaluation import RegressionMetrics
# from pyspark.mllib.evaluation import BinaryClassificationMetrics
# from pyspark.ml.tuning import ParamGridBuilder, CrossValidator, CrossValidatorModel
# from pyspark.ml.evaluation import RegressionEvaluator
# import seaborn as sns

DATA_LOCATION = "../data/raw/2022-06-05-UCIHD-001-AB12.csv"
analytics_save_location = "../data/processed/analytics"

def start_spark():
    appName = "ML-Analytics"
    master = "local"

    spark = SparkSession.builder.appName(appName).master(master).getOrCreate()
    sc = spark.sparkContext
    sqlContext = SQLContext(spark.sparkContext)
    return spark

# DELETE
# spark = start_spark()

# TODO: Add datatype requirements to user generated CSV of metadata
#   or use inferSchema=True during csv read
# df = spark.read.csv(path=DATA_LOCATION, inferSchema=True, header=True)

# define the schema, corresponding to a line in the csv data file.
def define_dataset_schema(data_location, dataset):
    schema = StructType([
        StructField("age", FloatType(), nullable=True),
        StructField("sex", FloatType(), nullable=True),
        StructField("chest_pain_type", FloatType(), nullable=True),
        StructField("resting_blood_pressure", FloatType(), nullable=True),
        StructField("cholesterol", FloatType(), nullable=True),
        StructField("fasting_blood_sugar", FloatType(), nullable=True),
        StructField("resting_electrocardiographic", FloatType(), nullable=True),
        StructField("max_heart_rate_achieved", FloatType(), nullable=True),
        StructField("exercise_induced_angina", FloatType(), nullable=True),
        StructField("ST_depression_induced_by_exercise", FloatType(), nullable=True),
        StructField("peak_exercise_st_slope", FloatType(), nullable=True),
        StructField("major_vessels_count", FloatType(), nullable=True),
        StructField("thalassemia", FloatType(), nullable=True),
        StructField("target", FloatType(), nullable=True)]
    )
    return schema

# DELETE
# schema = define_dataset_schema(data_location=None, dataset=None)

# NEW - reading dataset from HDFS

# HDFS_PARTITIONED_DIR = './data/processed' #TODO: change to "partitioned" after implement partition file
# dataset_to_analyze = '2022/06/UCIHD-001-LR' # directory of file to import for analysis #TODO: remove hardcoding
# client = InsecureClient('http://10.4.41.82:9870', user='bdm')  # this IP should be changed to your personal VM
# with client.read(f"{HDFS_PARTITIONED_DIR}/{dataset_to_analyze}") as reader:
#     df = spark.read.parquet(reader, schema=schema, header=True)
# df = spark.read.parquet(path="../data/raw/UCIHD-001-LR.parquet", schema=schema, header=True)


# Create a histogram of all items
# fig, axes = plt.subplots(4,4,figsize=(26,20))
# import pickle
# for index, columnName in enumerate(columns):
#     ax = axes.reshape(-1)[index]
#     boxplot = hdf.cols[columnName].hist(ax=ax)
#     pickle.dump(axes, open(f"{analytics_save_location}/{columnName}_histogram.pickle", "wb"))
# plt.show()


#Creating individual plots
# figure = plt.figure()
# hdf.cols['age'].hist()
# plt.show()


def read_dataset_for_analysis(spark_session, data_location, schema):
    df = spark_session.read.csv(path=data_location, schema=schema, header=True)
    return df

# convert to pandas and write to CSV
# summary file does not need to be distributed (small file)
# df.describe().write.csv(f"{analytics_save_location}/describe.csv")


def import_dataset_headers(data_location):
    headers = pd.read_csv("../data/test-data/headers.csv", header=None, names=["column_name"])
    columns = headers["column_name"].values.tolist()
    # TODO: Quality Check -> Do the names of the columns align?
    return columns


def generate_descriptive_analytics_files(columns, analysis_dataframe, analytics_save_location):
    result_df = analysis_dataframe.groupBy('target').count()
    result_df.show()
    analysis_dataframe.describe().toPandas().to_csv(f"{analytics_save_location}/describe.csv", index=False)

    hdf = analysis_dataframe.toHandy()
    hdf.show()
    hdf.isnull(ratio=True)

    for index, columnName in enumerate(columns):
        figure = plt.figure()
        hdf.cols[columnName].hist()
        # plt.show()
        plt.savefig(f"{analytics_save_location}/{columnName}_histogram.png", dpi=figure.dpi)
        pickle.dump(figure, open(f"{analytics_save_location}/{columnName}_histogram.pickle", "wb"))
        plt.close('all')


# DELETE
# df = read_dataset_for_analysis(DATA_LOCATION, schema)
# columns = import_dataset_headers(data_location=None)
# generate_descriptive_analytics_files(df)


### Data pre-processing
# All data submitted must be free of empty values and pre-processed by the user, so not cleaning, null value,
# reformatting, or imputing will take place.

# handy spark allows us to make use of visualization functions without reshuffling data or bringing it all into
# memory. It will process data in distributed way.





# from matplotlib import pyplot as plt
# fig, axs = plt.subplots(1, 4, figsize=(12, 4))
# hdf.cols['resting_blood_pressure'].boxplot(ax=axs[0])
# # hdf.cols['age'].boxplot(ax=axs[1])
# plt.show()

# df.take(5)

# fig, axs = plt.subplots(1, 4, figsize=(12, 4))
# hdf.cols['sex'].hist(ax=axs[0])
# # hdf.cols['age'].boxplot(ax=axs[1])
# plt.show()


def transform_data_to_target_schema(columns, analysis_dataframe):
    # move target value to beginning of dataframe so that it isn't impacted
    feature_column = columns[:-1] # target is always the last column
    columns = [columns[-1], *columns[:-1]] # move last item (target) to beginning
    # columns = ["target", "age", "sex", "chest_pain_type", "resting_blood_pressure", "cholesterol", "fasting_blood_sugar",
    #            "resting_electrocardiographic", "max_heart_rate_achieved", "exercise_induced_angina",
    #            "ST_depression_induced_by_exercise", "peak_exercise_st_slope", "major_vessels_count", "thalassemia"]
    df = analysis_dataframe.select(columns)
    assembler = VectorAssembler(inputCols=feature_column, outputCol="features")
    assembled_df = assembler.transform(df)

    standardScaler = StandardScaler(inputCol="features", outputCol="features_scaled")
    scaled_df = standardScaler.fit(assembled_df).transform(assembled_df)

    assembled_df.show(10, truncate=False)
    scaled_df.select("features", "features_scaled").show(10, truncate=False)

    train_data, test_data = scaled_df.randomSplit([.8, .2], seed=42)

    return train_data, test_data, feature_column


# DELETE
# train_data, test_data, feature_column = transform_data_to_target_schema(
#     columns=columns,
#     analysis_dataframe=df)

# def scala_data_on_features(transformed_data):
#     standardScaler = StandardScaler(inputCol="features", outputCol="features_scaled")
#     scaled_df = standardScaler.fit(transformed_data).transform(transformed_data)
#
#     scaled_df.select("features", "features_scaled").show(10, truncate=False)
#
#     return scaled_df

# # DELETE
# scala_data_on_features(
#     transformed_data=assembled_df)


# train_data, test_data = scaled_df.randomSplit([.8,.2], seed=42)



def integrate_parameters_and_build_LR_model(parameter_location, training_data):

    parameters = pd.read_csv(parameter_location)
    parameters_dict = parameters.to_dict('list')

    maxIter = int(parameters_dict["maxIter"][0])
    regParam = float(parameters_dict["regParam"][0])
    elasticNetParam = float(parameters_dict["elasticNetParam"][0])
    tol = float(parameters_dict["tol"][0])
    fitIntercept = bool(parameters_dict["fitIntercept"][0])
    standardization = bool(parameters_dict["standardization"][0])
    solver = str(parameters_dict["solver"][0])
    weightCol = None
    # weightCol = str(parameters_dict["weightCol"][0])
    aggregationDepth = int(parameters_dict["aggregationDepth"][0])
    loss = str(parameters_dict["loss"][0])
    epsilon = float(parameters_dict["epsilon"][0])

    #TODO: Issue with setting weightCol=None, throwing error. Removing this param option until fixed
    lr = (LinearRegression(featuresCol='features_scaled', labelCol="target", predictionCol='newPrediction'))
    lr.setParams(
        maxIter=maxIter,
        regParam=regParam,
        elasticNetParam=elasticNetParam,
        tol=tol,
        fitIntercept=fitIntercept,
        standardization=standardization,
        solver=solver,
        # weightCol=None,
        aggregationDepth=aggregationDepth,
        loss=loss,
        epsilon=epsilon
    )
    linearModel = lr.fit(training_data)

    return linearModel

# DELETE
# linearModel = integrate_parameters_and_build_LR_model(
#     parameter_location="../data/test-data/parameters.csv",
#     training_data=train_data)


def return_LR_model_parameters(LR_model, features):
    coeff_df = pd.DataFrame({"Feature": ["Intercept"] + features, "Co-efficients": np.insert(LR_model.coefficients.toArray(), 0, LR_model.intercept)})
    coeff_df = coeff_df[["Feature", "Co-efficients"]]
    return coeff_df


# DELETE
# coefficients = return_LR_model_parameters(
#     LR_model=linearModel,
#     features=feature_column)


def validate_LR_model(LR_model, testing_data):
    predictions = LR_model.transform(testing_data)

    predandlabels = predictions.select("newPrediction", "target")
    predandlabels.show()
    predandlabels_RDD = predandlabels.rdd

    metrics = MulticlassMetrics(predandlabels_RDD)

    precision = metrics.precision(1.0)
    recall = metrics.recall(1.0)
    f1Score = metrics.fMeasure(1.0)
    print("Summary Stats")
    print("Precision = %s" % precision)
    print("Recall = %s" % recall)
    print("F1 Score = %s" % f1Score)


def stop_spark(spark_session):
    spark_session.stop()
    print("spark session ended")

#DELETE
# validate_LR_model(
#     LR_model=linearModel,
#     testing_data=test_data)
# stop_spark()