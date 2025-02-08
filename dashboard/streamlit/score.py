import json
import numpy as np
import tensorflow as tf
from azureml.core.model import Model

def init():
    global model
    model_path = Model.get_model_path("CrimeSeverityMLPModel")
    model = tf.keras.models.load_model(model_path)

def run(raw_data):
    try:
        data = np.array(json.loads(raw_data)["data"])
        prediction = model.predict(data)
        predicted_class = np.argmax(prediction, axis=1).tolist()
        return json.dumps({"crime_severity": predicted_class})
    except Exception as e:
        return json.dumps({"error": str(e)})