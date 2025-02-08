from pyspark.sql import SparkSession
from pyspark.sql.functions import col, unix_timestamp, lpad, substring
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, MinMaxScaler
from pyspark.ml import Pipeline

# Azure Storage Configuration
storage_account_name = "crimeprojectstorage"
storage_account_key = "storage key placeholder"
container_name = "crime-data"
mount_point = "/mnt/crime_data"

# Mount Azure Blob Storage
dbutils.fs.mount(
    source=f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net",
    mount_point=mount_point,
    extra_configs={f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net": storage_account_key}
)

# Initialize Spark Session
spark = SparkSession.builder.appName("CrimeDataProcessing").getOrCreate()

# Load and preprocess data
df = spark.read.csv(
    "dbfs:/mnt/crime_data/Crime_Data_from_2020_to_Present.csv", 
    header=True, 
    inferSchema=True
).select([
    'Date Rptd', 'DATE OCC', 'Vict Age', 'Crm Cd Desc', 
    'AREA NAME', 'Vict Sex', 'Part 1-2', 'TIME OCC', 'LAT', 'LON'
]).dropna()

# Feature Engineering Pipeline
df = (df
      .withColumn("Date Rptd", unix_timestamp(col("Date Rptd")).cast("double"))
      .withColumn("DATE OCC", unix_timestamp(col("DATE OCC")).cast("double"))
      .withColumn("TIME OCC", lpad(col("TIME OCC").cast("int").cast("string"), 4, "0"))
      .withColumn("HOUR OCC", substring(col("TIME OCC"), 1, 2).cast("int").cast("double"))
      .withColumn("TIME OCC", col("TIME OCC").cast("double")))

numeric_cols = ["Date Rptd", "DATE OCC", "Vict Age", "TIME OCC", "HOUR OCC", "LAT", "LON"]
categorical_cols = ["Crm Cd Desc", "AREA NAME", "Vict Sex"]

stages = [
    *[StringIndexer(inputCol=c, outputCol=f"{c}_index") for c in categorical_cols],
    *[OneHotEncoder(inputCol=f"{c}_index", outputCol=f"{c}_encoded") for c in categorical_cols],
    VectorAssembler(inputCols=numeric_cols + [f"{c}_encoded" for c in categorical_cols], outputCol="features"),
    MinMaxScaler(inputCol="features", outputCol="scaled_features")
]

processed_df = Pipeline(stages=stages).fit(df).transform(df)
processed_df.select("scaled_features", "Part 1-2").write.mode("overwrite").parquet("dbfs:/mnt/crime_data/processed_data")