from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from config import KAFKA_CONFIG, AZURE_CONFIG
import json
from event_processor import process_batch

def create_spark_streaming_context():
    """Initialize Spark Streaming Context with Kafka integration"""
    spark = SparkSession.builder \
        .appName("CrimeStreamProcessor") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()
    
    ssc = StreamingContext(spark.sparkContext, 10)  # 10-second batches
    
    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_CONFIG['bootstrap_servers']) \
        .option("subscribe", KAFKA_CONFIG['input_topic']) \
        .option("startingOffsets", "latest") \
        .load()
    
    return ssc, kafka_stream

def start_streaming():
    """Start real-time crime report processing"""
    ssc, stream = create_spark_streaming_context()
    
    # Process each batch with schema validation and model prediction
    stream.writeStream \
        .foreachBatch(process_batch) \
        .option("checkpointLocation", AZURE_CONFIG['checkpoint_path']) \
        .start() \
        .awaitTermination()

if __name__ == "__main__":
    start_streaming()