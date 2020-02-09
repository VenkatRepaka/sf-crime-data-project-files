import logging
import logging.config
from configparser import ConfigParser
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf


# TODO Create a schema for incoming resources
schema = StructType([
    StructField("crime_id", StringType(), True),
    StructField("original_crime_type_name", StringType(), True),
    StructField("report_date", StringType(), True),
    StructField("call_date", StringType(), True),
    StructField("offense_date", StringType(), True),
    StructField("call_time", StringType(), True),
    StructField("call_date_time", TimestampType(), True),
    StructField("disposition", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("agency_id", StringType(), True),
    StructField("address_type", StringType(), True),
    StructField("common_location", StringType(), True)
])

radio_schema = StructType([
    StructField("disposition_code", StringType(), True),
    StructField("description", StringType(), True)
])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark \
        .readStream \
        .format("kafka") \
        .option("subscribe", "org.sf.crime.police.service.calls") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", "200") \
        .option("stopGracefullyOnShutdown", "true") \
        .load()


    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value AS STRING)")

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("DF.*")

    # TODO select original_crime_type_name and disposition
    distinct_table = service_table.select("original_crime_type_name", "disposition", "call_date_time") \
                        .distinct() \
                        .dropna() \
                        .withWatermark("call_date_time", "60 minutes")
    distinct_table.printSchema()
    
#     distinct_query = distinct_table \
#                 .writeStream \
#                 .format("console") \
#                 .queryName("distinct_query") \
#                 .start()
    
#     distinct_query.awaitTermination()
    

    # count the number of original crime type
#     agg_df = distinct_table.dropna()
#                 .select("original_crime_type_name")
#                 .agg({"original_crime_type_name": "count"})
#                 .withColumnRenamed("count(original_crime_type_name)", "crime_count")
#                 .orderby(desc("crime_count"))
    agg_df = distinct_table \
                .groupBy("original_crime_type_name", psf.window(distinct_table.call_date_time, "10 minutes", "5 minutes")) \
                .count() \
                .withColumnRenamed("count", "crime_count") \
                .sort(psf.desc("crime_count"))
    agg_df.printSchema()
                

    # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # TODO write output stream
    query = agg_df \
                .writeStream \
                .format("console") \
                .queryName("crime_count") \
                .outputMode("complete") \
                .start()


    # TODO attach a ProgressReporter
#     query.awaitTermination()

    # TODO get the right radio code json path
    radio_code_json_filepath = "./radio_code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath, schema=radio_schema)

    # clean up your data so that the column names match on radio_code_df and agg_df
    # we will want to join on the disposition code

    # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")
    radio_code_df.printSchema()

    # TODO join on disposition column
    join_query = distinct_table.join(radio_code_df, "disposition", "left") \
                    .select("disposition", "original_crime_type_name", "call_date_time") \
                    .writeStream \
                    .format("console") \
                    .queryName("radio-service-disposition") \
                    .start()


    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .config("spark.ui.port", "3000") \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel('ERROR')

    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()
