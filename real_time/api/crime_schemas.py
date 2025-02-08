from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CrimeReportInput(BaseModel):
    """Schema for incoming crime reports from external systems"""
    crime_type: str
    coordinates: dict  # {"lat": float, "lon": float}
    timestamp: datetime
    area_name: str
    victim_age: int
    victim_sex: Optional[str] = None
    weapon_used: Optional[str] = None

class CrimePredictionOutput(BaseModel):
    """Schema for model prediction responses"""
    report_id: str
    severity_level: int  # 0=Low, 1=Medium, 2=High
    confidence_score: float
    recommended_response: str

class KafkaCrimeSchema:
    """Avro schema definition for Kafka message serialization"""
    schema_str = """
    {
        "type": "record",
        "name": "CrimeReport",
        "fields": [
            {"name": "crime_type", "type": "string"},
            {"name": "coordinates", "type": {"type": "record", "name": "GeoPoint", 
                "fields": [
                    {"name": "lat", "type": "double"},
                    {"name": "lon", "type": "double"}
                ]}},
            {"name": "timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}},
            {"name": "area_name", "type": "string"},
            {"name": "victim_age", "type": "int"}
        ]
    }
    """

def load_avro_schema(schema_path: str = "schemas/crime_report.avsc") -> dict:
    """Load Avro schema from file for schema registry integration"""
    # Implementation would use confluent_kafka.schema_registry
    return {
        "schema": KafkaCrimeSchema.schema_str,
        "schema_type": "AVRO"
    }