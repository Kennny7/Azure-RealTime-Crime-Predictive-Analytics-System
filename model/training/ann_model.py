import mlflow
import mlflow.tensorflow
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from pyspark.sql import SparkSession
from pyspark.ml.functions import vector_to_array
from sklearn.model_selection import train_test_split

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# Load processed data
df = spark.read.parquet("dbfs:/mnt/crime_data/processed_data")
pdf = df.select(
    vector_to_array("scaled_features").alias("features"),
    col("Part 1-2").cast("float")
).toPandas()

# Prepare features and labels
X = np.array(pdf["features"].tolist())
y = np.where(pdf["Part 1-2"].values == 1, 0, 1)  # Binary encoding

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Model architecture
def build_model(input_shape):
    model = Sequential([
        Dense(512, activation='relu', input_shape=(input_shape,)),
        BatchNormalization(),
        Dropout(0.5),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.4),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), 
                tf.keras.metrics.Recall(), tf.keras.metrics.AUC()]
    )
    return model

# MLflow tracking setup
mlflow.set_experiment("/Users/username@domain.com/crime_detection_experiment")

with mlflow.start_run():
    model = build_model(X_train.shape[1])
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=256,
        callbacks=[
            EarlyStopping(monitor='val_auc', patience=10, mode='max'),
            ModelCheckpoint("best_model.keras", save_best_only=True)
        ],
        class_weight={0: 1, 1: 2}
    )
    
    # Log model and metrics
    mlflow.tensorflow.log_model(model, "model")
    mlflow.log_params({
        "batch_size": 256,
        "learning_rate": 0.0001,
        "architecture": "512-256-128"
    })