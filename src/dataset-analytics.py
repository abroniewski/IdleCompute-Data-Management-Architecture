import os
import pandas as pd
import numpy as np

import handyspark

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession, SQLContext

from pyspark.sql.types import *
import pyspark.sql.functions as F
from pyspark.sql.functions import udf, col

from pyspark.ml.regression import LinearRegression
from pyspark.mllib.evaluation import RegressionMetrics

from pyspark.ml.tuning import ParamGridBuilder, CrossValidator, CrossValidatorModel
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.evaluation import RegressionEvaluator

#import copied from landing-zone
import os
from os.path import join
import re
from pyarrow import json, csv
import pyarrow.parquet as pq
from hdfs import InsecureClient
from tqdm import tqdm

#%%
import seaborn as sns
import matplotlib.pyplot as plt

#%%
appName = "ML-Analytics"
master = "local"

spark = SparkSession.builder.appName(appName).master(master).getOrCreate()
sc = spark.sparkContext
sqlContext = SQLContext(spark.sparkContext)

#%%
# TODO: Add datatype requirements to user generated CSV of metadata
#   or use inferSchema=True during csv read
# df = spark.read.csv(path=DATA_LOCATION, inferSchema=True, header=True)

# define the schema, corresponding to a line in the csv data file.

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

#%%
DATA_LOCATION = "../data/raw/2022-06-05-UCIHD-001-AB12.csv"
analytics_save_location = "../data/processed/analytics"
df = spark.read.csv(path=DATA_LOCATION, schema=schema, header=True)

#%%
# NEW - reading dataset from HDFS

# HDFS_PARTITIONED_DIR = './data/processed' #TODO: change to "partitioned" after implement partition file
# dataset_to_analyze = '2022/06/UCIHD-001-LR' # directory of file to import for analysis #TODO: remove hardcoding
# client = InsecureClient('http://10.4.41.82:9870', user='bdm')  # this IP should be changed to your personal VM
# with client.read(f"{HDFS_PARTITIONED_DIR}/{dataset_to_analyze}") as reader:
#     df = spark.read.parquet(reader, schema=schema, header=True)
# df = spark.read.parquet(path="../data/raw/UCIHD-001-LR.parquet", schema=schema, header=True)



#%%

# TODO: Convert to RDD map/reduce function
result_df = df.groupBy('target').count()
result_df.show()

#%%
# convert to pandas and write to CSV
# summary file does not need to be distributed (small file)
# df.describe().write.csv(f"{analytics_save_location}/describe.csv")
df.describe().toPandas().to_csv(f"{analytics_save_location}/describe.csv", index=False)

#%%

### Data pre-processing
# All data submitted must be free of empty values and pre-processed by the user, so not cleaning, null value,
# reformatting, or imputing will take place.

# handy spark allows us to make use of visualization functions without reshuffling data or bringing it all into
# memory. It will process data in distributed way.
hdf = df.toHandy()

#%%

hdf.show()
hdf.isnull(ratio=True)

#%%
headers = pd.read_csv("../data/test-data/headers.csv", header=None, names=["column_name"])
columns = headers["column_name"].values.tolist()
columns[1]

#%%
import pickle
# Create a histogram of all items
fig, axes = plt.subplots(4,4,figsize=(26,20))

for index, columnName in enumerate(columns):
    ax = axes.reshape(-1)[index]
    boxplot = hdf.cols[columnName].hist(ax=ax)
    pickle.dump(axes, open(f"{analytics_save_location}/{columnName}_histogram.pickle", "wb"))
plt.show()

#%%

#Creating individual plots
figure = plt.figure()
hdf.cols['age'].hist()
plt.show()
#%%
for index, columnName in enumerate(columns):
    figure = plt.figure()
    hdf.cols[columnName].hist()
    # plt.show()
    plt.savefig(f"{analytics_save_location}/{columnName}_histogram.png", dpi=figure.dpi)
    pickle.dump(figure, open(f"{analytics_save_location}/{columnName}_histogram.pickle", "wb"))

#%%

from matplotlib import pyplot as plt
fig, axs = plt.subplots(1, 4, figsize=(12, 4))
hdf.cols['resting_blood_pressure'].boxplot(ax=axs[0])
# hdf.cols['age'].boxplot(ax=axs[1])
plt.show()

#%%
df.take(5)
#%%
fig, axs = plt.subplots(1, 4, figsize=(12, 4))
hdf.cols['sex'].hist(ax=axs[0])
# hdf.cols['age'].boxplot(ax=axs[1])
plt.show()

#%%

### standardize values
# move target value to beginning of dataframe so that it isn't impacted
feature_column = columns[:-1] # target is always the last column
columns = [columns[-1], *columns[:-1]] # move last item (target) to beginning
# columns = ["target", "age", "sex", "chest_pain_type", "resting_blood_pressure", "cholesterol", "fasting_blood_sugar",
#            "resting_electrocardiographic", "max_heart_rate_achieved", "exercise_induced_angina",
#            "ST_depression_induced_by_exercise", "peak_exercise_st_slope", "major_vessels_count", "thalassemia"]
df = df.select(columns)


assembler = VectorAssembler(inputCols=feature_column, outputCol="features")

assembled_df = assembler.transform(df)

assembled_df.show(10, truncate=False)
#%%

standardScaler = StandardScaler(inputCol="features", outputCol="features_scaled")
scaled_df = standardScaler.fit(assembled_df).transform(assembled_df)
scaled_df.select("features", "features_scaled").show(10, truncate=False)
#%%

train_data, test_data = scaled_df.randomSplit([.8,.2], seed=42)

#%%

lr = (LinearRegression(featuresCol='features_scaled', labelCol="target", predictionCol='predmedhv',
                               maxIter=10, regParam=0.3, elasticNetParam=0.8, standardization=False))
linearModel = lr.fit(train_data)
#%%

linearModel.coefficients
linearModel.intercept
#%%

coeff_df = pd.DataFrame({"Feature": ["Intercept"] + feature_column, "Co-efficients": np.insert(linearModel.coefficients.toArray(), 0, linearModel.intercept)})
coeff_df = coeff_df[["Feature", "Co-efficients"]]
coeff_df

#%%
predictions = linearModel.transform(test_data)
#%%
predandlabels = predictions.select("predmedhv", "target")
predandlabels.show()
#%%