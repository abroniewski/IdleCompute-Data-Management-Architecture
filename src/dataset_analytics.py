import pandas as pd
import numpy as np

from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import LinearRegression
from pyspark.mllib.evaluation import RegressionMetrics

import handyspark

import matplotlib.pyplot as plt
import pickle
import os
import shutil


def start_spark():
    appName = "ML-Analytics"
    master = "local"

    spark = SparkSession.builder.appName(appName).master(master).getOrCreate()
    sc = spark.sparkContext
    # sc.setLogLevel("OFF")
    sqlContext = SQLContext(spark.sparkContext)
    print("SparkSession initialized")
    return spark


# TODO: Quality Check -> Do the names of the columns align?
def import_dataset_headers(data_location):
    headers = pd.read_csv("../data/test-data/headers.csv", header=None, names=["column_name"])
    columns = headers["column_name"].values.tolist()

    return columns


# TODO: Add datatype requirements to user headers CSV of metadata.
#   Read datatype from csv and iterate through similar to other functions.
# inferSchema=True during csv read can read to failed training if inference is
# incorrect
def define_dataset_schema(data_location, dataset, data_type):
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


def read_dataset_for_analysis(spark_session, data_location, schema):
    df = spark_session.read.csv(path=data_location, schema=schema, header=True)
    print(f"Data loaded from {data_location}")
    return df


def read_parquet_dataset_for_analysis(spark_session, data_location):
    # df = spark_session.read.csv(path=data_location, schema=schema, header=True)
    df = spark_session.read.parquet(data_location)
    dataset_rdd = df.rdd.map(lambda x: (x[0]))
    # df = dataset_rdd.map(lambda x: (x,)).toDF()
    df = dataset_rdd.toDF()
    # df = dataset_rdd2.toDF()

    print(f"Parquet data loaded from {data_location}")
    return df

    # data_location = 'data/partitioned/2022/03/VKY001-002-AB12'


def generate_descriptive_analytics_files(columns, analysis_dataframe, analytics_save_location):
    print("Beginning descriptive analytics")

    plots_dir = os.path.join(analytics_save_location, "plots")
    plots_serialized_dir = os.path.join(analytics_save_location, "plots_serialized")
    if not os.path.exists(analytics_save_location):  # Check if analytics save path exists
        plots_dir = os.path.join(analytics_save_location, "plots")
        plots_serialized_dir = os.path.join(analytics_save_location, "plots_serialized")
        # Create a new directory if needed
        os.makedirs(plots_dir)  # path where histogram plots are written
        os.makedirs(plots_serialized_dir)  # path where serialized plots are written
        print(f"New directories created:")
        print(f"    {analytics_save_location}")
        print(f"    {plots_dir}")
        print(f"    {plots_serialized_dir}")

    describe_file_path = os.path.join(analytics_save_location, "dataset_describe.csv")
    analysis_dataframe.describe().toPandas().to_csv(describe_file_path, index=False)  # write data summary to file

    hdf = analysis_dataframe.toHandy()  # HandySpark used for visualizations while parallelized

    for index, columnName in enumerate(columns):  # each plot written individually
        figure = plt.figure()
        hdf.cols[columnName].hist()

        hist_file_path = os.path.join(plots_dir, f"{columnName}_histogram.png")
        pickle_file_path = os.path.join(plots_serialized_dir, f"{columnName}_histogram.pickle")

        plt.savefig(hist_file_path, dpi=figure.dpi)  # save as ".png file"
        pickle.dump(figure, open(pickle_file_path, "wb"))  # save as serializable ".pickle" file
        plt.close('all')
    print(f"\nDescriptive analytics figures generated to: {analytics_save_location}")
    print("Target variable count is:")


### Data pre-processing
# All data submitted must be free of empty values and pre-processed by the user, so not cleaning, null value,
# reformatting, or imputing will take place.

# HandySpark allows us to make use of visualization functions without reshuffling data or bringing it all into
# memory. It will process data in distributed way.


def transform_data_to_target_schema(columns, analysis_dataframe):
    # move target value to beginning of dataframe so that it isn't impacted by transform
    feature_column = columns[:-1]  # target is always the last column
    columns = [columns[-1], *columns[:-1]]  # move last item (target) to beginning

    df = analysis_dataframe.select(columns)
    assembler = VectorAssembler(inputCols=feature_column, outputCol="features")
    assembled_df = assembler.transform(df)  # creating vector of feature columns for model training

    standardScaler = StandardScaler(inputCol="features", outputCol="features_scaled")
    scaled_df = standardScaler.fit(assembled_df).transform(assembled_df)  # scaling data

    train_data, test_data = scaled_df.randomSplit([.8, .2], seed=42)  # creating test/train split

    print("Dataset transformed and split into train/test set")
    print(f"Number of features: {len(feature_column)}")
    return train_data, test_data, feature_column


def integrate_parameters_and_build_LR_model(parameter_location, training_data, analytics_save_location):

    parameters = pd.read_csv(parameter_location)  # parameters to be passed to model
    parameters_dict = parameters.to_dict('list')

    # ensure each parameter is of the correct type
    # TODO: Issue with setting weightCol=None, throwing error. Removing this param option until fixed
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

    print("Linear regression model trained")

    model_file_path = os.path.join(analytics_save_location, "model/LR_model")
    if os.path.exists(model_file_path):
        shutil.rmtree(model_file_path)  # remove existing model if code re-run
    linearModel.save(model_file_path)
    print(f"Linear regression model saved to: {model_file_path}")

    return linearModel


def validate_LR_model(LR_model, testing_data, analytics_save_location):
    predictions = LR_model.transform(testing_data)

    predandlabels = predictions.select("newPrediction", "target")
    predandlabels_RDD = predandlabels.rdd
    predandlabels_RDD2 = predandlabels_RDD.map(lambda x: (x[0], float(x[1])))  #convert filetype from double to float

    metrics = RegressionMetrics(predandlabels_RDD2)

    meanAbsoluteError = metrics.meanAbsoluteError
    meanSquaredError = metrics.meanSquaredError
    rootMeanSquaredError = metrics.rootMeanSquaredError
    r2 = metrics.r2

    summary_headers = ["meanAbsoluteError", "meanSquaredError", "rootMeanSquaredError", "r2"]
    summary_stats = [meanAbsoluteError, meanSquaredError, rootMeanSquaredError, r2]
    summary = pd.DataFrame(list(zip(summary_headers, summary_stats)))

    metrics_file_path = os.path.join(analytics_save_location, "LR_model_accuracy.csv")
    summary.to_csv(metrics_file_path, index=False, header=None)

    print("Validation data exported.")

def stop_spark(spark_session):
    spark_session.stop()
    print("spark session ended")