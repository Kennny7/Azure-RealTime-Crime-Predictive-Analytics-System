import requests
import json

endpoint_url = "<your-endpoint-url>"

sample_data = {
    "data": [[0.5, 0.2, 30, 1200, 14, 34.05, -118.25]]  # Example input
}

response = requests.post(endpoint_url, json=sample_data)
print(response.json())