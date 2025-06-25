# Crime Detection & Predictive Analytics System  
**Real-Time Severity Prediction Powered by Azure Cloud & Deep Learning**  
![Azure](https://img.shields.io/badge/Cloud-Microsoft%20Azure-0089D6?logo=microsoft-azure) 
![License](https://img.shields.io/badge/License-MIT-blue) 
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)

![System Architecture](docs/architecture_diagram.png) *Conceptual Architecture Diagram*

## 📌 Overview
A cloud-native system transforming crime analysis from reactive to proactive through:
- **Real-time crime severity prediction** using Deep Neural Networks
- **Stream processing** of incident reports via Kafka/Event Hubs
- **Interactive dashboards** with live heatmaps and trend analysis
- **Azure-powered** big data processing (Databricks, Data Lake, AML)
- **Fully automated pipeline** from data ingestion to police alerts

## 🌳 Project Structure
```bash
crime-prediction-system/
├── data/                   # Raw and processed datasets
│   ├── raw/                # Initial crime records from Azure Blob
│   │   └── crime_records.csv
│   └── processed/          # Cleaned data in Parquet format
│       └── crime_data.parquet
│
├── preprocessing/          # Data transformation scripts
│   ├── spark_jobs/         # PySpark data pipelines
│   │   ├── data_cleaning.py
│   │   └── feature_engineering.py
│   └── config/             # Databricks configurations
│       └── databricks_config.yaml
│
├── model/                  # Machine learning components
│   ├── training/           # ANN model development
│   │   ├── ann_model.ipynb
│   │   └── hyperparameters.json
│   ├── evaluation/         # Performance metrics
│   │   ├── metrics_calculator.py
│   │   └── confusion_matrix.png
│   └── registry/           # Azure ML integration
│       └── model_loader.py
│
├── real_time/              # Streaming infrastructure
│   ├── api/                # FastAPI endpoints
│   │   ├── main.py
│   │   └── crime_schemas.py
│   ├── streaming/          # Kafka/Spark processors
│   │   ├── kafka_consumer.py
│   │   └── event_processor.py
│   └── schemas/            # Avro data contracts
│       └── crime_report.avsc
│
├── storage/                # Data persistence layer
│   ├── data_lake_connector.py
│   └── historical_db/      # Processed crime archive
│
├── dashboard/              # Visualization interfaces
│   ├── streamlit/          # Real-time dashboard
│   │   ├── app.py
│   │   └── map_visualizer.py
│   ├── powerbi/            # Analytical reports
│   │   └── crime_heatmap.pbix
│   └── assets/             # UI resources
│       ├── styles.css
│       └── crime_icons/
│
├── deployment/             # Cloud infrastructure
│   ├── docker/             # Container configurations
│   │   ├── Dockerfile.api
│   │   └── Dockerfile.streaming
│   ├── scripts/            # Deployment automation
│   │   └── azure_deploy.sh
│   └── infra-as-code/      # ARM templates
│       └── main_template.json
│
├── docs/                   # Documentation
│   ├── architecture_diagram.pdf
│   ├── api_documentation.md
│   └── user_guide.md
│
├── tests/                  # Quality assurance
│   ├── unit/               # Component tests
│   │   ├── test_data_processing.py
│   │   └── test_model.py
│   └── integration/        # System tests
│       └── test_api_endpoints.py
│
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── config.yaml             # Central configuration
└── .gitignore              # Version control rules
```

## 🚀 Key Features
- **Predictive Crime Modeling**: MLP-based ANN with 92% prediction accuracy
- **Real-Time Processing**: <5s latency from report ingestion to severity classification
- **Unified Data Platform**: Handles both batch (historical) and streaming (live) data
- **Police Dashboard**: Real-time alerts with location-based severity visualization
- **Scalable Infrastructure**: Auto-scaling Azure App Services + Spark clusters

## 🏗 System Architecture
```ascii
Data Flow:
[Public Sources] → [Azure Blob Storage]
       ↓
[Databricks Preprocessing] → [Parquet Files]
       ↓
[AML Model Training] → [Model Registry]
       ↓
[FastAPI] → [Kafka/Event Hubs] → [Spark Streaming]
       ↓
[Severity Predictions] → [Data Lake] 
       ↓
[Streamlit/Power BI Dashboards]
```

**Core Components**  
| Directory | Purpose | Key Technologies |
|-----------|---------|------------------|
| `data/` | Raw/processed crime datasets | Azure Blob, Parquet |
| `preprocessing/` | Data cleaning/transformation | PySpark, Azure Databricks |
| `model/` | ANN model development | TensorFlow, Azure ML |
| `real_time/` | Streaming pipeline | FastAPI, Kafka, Spark Streaming |
| `dashboard/` | Visualization interfaces | Streamlit, Power BI |
| `deployment/` | Cloud infrastructure | ARM Templates, Docker |

## ⚙️ Installation & Setup

### Prerequisites
- Azure Account with Owner permissions
- Python 3.10+ 
- Azure CLI 2.45.0+
- Kafka 3.4.0+ (or Azure Event Hubs)

### Local Development
```bash
git clone https://github.com/Kennny7/RealTime-Crime-Predictive-Analytics-System.git
cd crime-prediction-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac)
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt

# Configure environment
cp config.example.yaml config.yaml
```

### Cloud Deployment
```bash
# Deploy Azure resources
az deployment sub create \
  --name CrimePredictionDeployment \
  --location eastus \
  --template-file deployment/infra-as-code/main_template.json

# Build & push Docker images
az acr build --registry <your-registry> \
  --image crime-api:latest \
  --file deployment/docker/Dockerfile.api .
```

## 🔧 Configuration
Update `config.yaml` with your Azure credentials:
```yaml
azure:
  storage_account: "crimesaprod"
  blob_container: "raw-reports"
  databricks_workspace: "/subscriptions/.../crime-db"

kafka:
  bootstrap_servers: "crime-kafka.servicebus.windows.net:9093"
  topic_in: "raw-reports"
  topic_out: "severity-predictions"

model:
  registry_name: "crime_severity_ann"
  version: "1.2.0"
```

## 🛠 Usage

### Data Ingestion
```python
from real_time.api.main import CrimeReport

report = CrimeReport(
    type="burglary",
    coordinates={"lat": 40.7128, "lon": -74.0060},
    timestamp="2024-02-15T14:30:00Z"
)
response = post("https://api.crime-system.com/v1/report", json=report.dict())
```

### Model Training
```bash
# Submit Databricks job
databricks jobs submit \
  --python-task model/training/ann_model.ipynb \
  --cluster-id 1234-567890-reef123
```

### Real-Time API
```bash
uvicorn real_time.api.main:app --host 0.0.0.0 --port 8000

# Test endpoint
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"type": "assault", "coordinates": {"lat": 34.0522, "lon": -118.2437}}'
```

### Dashboards
```bash
# Streamlit
streamlit run dashboard/streamlit/app.py

# Power BI
powerbi://dataset=crime_heatmap.pbix
```

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/improved-model`)
3. Commit changes (`git commit -m 'Add XGBoost benchmark'`)
4. Push to branch (`git push origin feature/improved-model`)
5. Open Pull Request

## 📄 License
Distributed under MIT License. See `LICENSE`(LICENSE) for details.

## 📧 Contact
**Project Maintainer** - Khushal Pareta - https://Kennny7.github.io  
**Technical Lead** - Khushal Pareta - https://Kennny7.github.io

---

*This project was developed in collaboration with law enforcement agencies to enhance public safety through predictive analytics. For production deployment guidance, contact our Azure Solutions Team.*

