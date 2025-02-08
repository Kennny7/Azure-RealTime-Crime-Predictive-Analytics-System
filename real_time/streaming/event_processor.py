from pyspark.sql import DataFrame
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import mlflow
import json
from config import KAFKA_CONFIG, MODEL_CONFIG
from confluent_kafka import Producer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CrimeEventProcessor")

# Load Avro schema equivalent for Spark
crime_schema = StructType([
    StructField("crime_type", StringType()),
    StructField("coordinates", StructType([
        StructField("lat", DoubleType()),
        StructField("lon", DoubleType())
    ])),
    StructField("timestamp", TimestampType()),
    StructField("area_name", StringType()),
    StructField("victim_age", IntegerType())
])

# Load production model
model = mlflow.pyfunc.load_model(f"models:/{MODEL_CONFIG['registry_name']}/{MODEL_CONFIG['production_stage']}")

kafka_producer = Producer({
    'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': '$ConnectionString',
    'sasl.password': KAFKA_CONFIG['connection_string']
})

def process_batch(df: DataFrame, batch_id: int):
    """Process real-time crime reports with validation and prediction"""
    try:
        if df.isEmpty():
            logger.info(f"Batch {batch_id}: No new reports")
            return

        # Parse JSON payload with schema validation
        parsed_df = df.select(
            from_json(col("value").cast("string"), crime_schema).alias("data")
        ).select("data.*").dropna()

        if parsed_df.isEmpty():
            logger.warning(f"Batch {batch_id}: All records failed schema validation")
            return

        # Prepare features for model
        processed_data = parsed_df.select(
            col("crime_type"),
            col("coordinates.lat").alias("lat"),
            col("coordinates.lon").alias("lon"),
            col("timestamp").cast("double"),
            col("area_name"),
            col("victim_age")
        ).toPandas()

        # Generate predictions
        predictions = model.predict(processed_data)

        # Publish predictions to Kafka
        for idx, row in processed_data.iterrows():
            message = {
                "coordinates": {"lat": row["lat"], "lon": row["lon"]},
                "severity": float(predictions[idx]),
                "crime_type": row["crime_type"],
                "timestamp": str(row["timestamp"])
            }
            kafka_producer.produce(
                KAFKA_CONFIG['output_topic'],
                value=json.dumps(message).encode('utf-8')
            )
        kafka_producer.flush()

        logger.info(f"Batch {batch_id}: Processed {len(predictions)} reports")

    except Exception as e:
        logger.error(f"Batch {batch_id} failed: {str(e)}")
        # Implement dead-letter queue logic here