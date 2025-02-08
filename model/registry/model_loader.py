import mlflow
import azureml.mlflow
from config import AZURE_ML_CONFIG  # Assume config.yaml contains these values

def register_azureml_model(model_path: str, model_name: str):
    """Register trained model in Azure ML Model Registry"""
    mlflow.set_tracking_uri(AZURE_ML_CONFIG["tracking_uri"])
    mlflow.set_experiment(AZURE_ML_CONFIG["experiment_name"])
    
    with mlflow.start_run():
        mlflow.tensorflow.log_model(
            tf_model=model_path,
            artifact_path="model",
            registered_model_name=model_name
        )
    print(f"Model {model_name} registered in Azure ML")

def load_production_model(model_name: str):
    """Load model from Azure ML Model Registry"""
    mlflow.set_tracking_uri(AZURE_ML_CONFIG["tracking_uri"])
    return mlflow.pyfunc.load_model(
        model_uri=f"models:/{model_name}/Production"
    )

# Example configuration in config.yaml:
# azure_ml:
#   tracking_uri: "azureml://eastus.api.azureml.ms/mlflow/v1.0/subscriptions/.../workspaces/crime_ml_workspace"
#   experiment_name: "/Users/Username@Domain.com/crime_detection_experiment"