from fastapi import FastAPI
from pydantic import BaseModel
from confluent_kafka import Producer
import json
from config import KAFKA_CONFIG

app = FastAPI(title="Crime Reporting API")

class CrimeReport(BaseModel):
    crime_type: str
    coordinates: dict  # {"lat": float, "lon": float}
    timestamp: str  # ISO 8601 format
    area_name: str
    victim_age: int

@app.post("/report")
async def submit_report(report: CrimeReport):
    """Endpoint for submitting new crime reports"""
    producer = Producer({
        'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': '$ConnectionString',
        'sasl.password': KAFKA_CONFIG['connection_string']
    })
    
    try:
        producer.produce(
            KAFKA_CONFIG['input_topic'],
            value=json.dumps(report.dict()).encode('utf-8')
        )
        producer.flush()
        return {"status": "Report queued for processing"}
    except Exception as e:
        return {"error": str(e)}