import mlflow
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_auc_score, roc_curve, precision_recall_curve,
    average_precision_score
)
import seaborn as sns
from pyspark.sql import SparkSession

def load_test_data():
    """Load processed data from Azure Data Lake"""
    spark = SparkSession.builder.getOrCreate()
    return spark.read.parquet("dbfs:/mnt/crime_data/processed_data") \
        .select("scaled_features", "Part 1-2") \
        .cache()

def evaluate_model(model, X_test, y_test):
    """Generate comprehensive evaluation metrics"""
    y_pred_proba = model.predict(X_test).flatten()
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    return {
        'roc_auc': roc_auc_score(y_test, y_pred_proba),
        'average_precision': average_precision_score(y_test, y_pred_proba),
        'classification_report': classification_report(y_test, y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred)
    }

def generate_evaluation_plots(y_true, y_pred_proba):
    """Create diagnostic visualization plots"""
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    ax[0].plot(fpr, tpr, label=f"AUC = {roc_auc_score(y_true, y_pred_proba):.2f}")
    ax[0].set_title('ROC Curve')
    
    # Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
    ax[1].plot(recall, precision, label=f"AP = {average_precision_score(y_true, y_pred_proba):.2f}")
    ax[1].set_title('Precision-Recall Curve')
    
    return fig

def log_to_mlflow(metrics, fig):
    """Log evaluation results to MLflow"""
    with mlflow.start_run():
        mlflow.log_metrics({
            'roc_auc': metrics['roc_auc'],
            'average_precision': metrics['average_precision']
        })
        mlflow.log_text(metrics['classification_report'], "classification_report.txt")
        mlflow.log_figure(fig, "evaluation_plots.png")
        mlflow.log_dict(
            {"confusion_matrix": metrics['confusion_matrix'].tolist()},
            "confusion_matrix.json"
        )

if __name__ == "__main__":
    # Load production model
    model = mlflow.tensorflow.load_model("models:/crime_severity_mlp/Production")
    
    # Prepare test data
    test_df = load_test_data().toPandas()
    X_test = np.array(test_df["scaled_features"].tolist())
    y_test = np.where(test_df["Part 1-2"].values == 1, 0, 1)
    
    # Execute evaluation
    metrics = evaluate_model(model, X_test, y_test)
    fig = generate_evaluation_plots(y_test, model.predict(X_test).flatten())
    
    # Log results
    log_to_mlflow(metrics, fig)
    print("Evaluation results logged to MLflow")