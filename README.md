# Mobile API Misuse Detector

An active-security platform for detecting API abuse in mobile applications using unsupervised machine learning.

## Overview

Mobile API Misuse Detector is a comprehensive security platform that combines real-time log ingestion, unsupervised anomaly detection (Isolation Forest), and a responsive web interface to automatically identify and alert on anomalous API usage in mobile applications.

**Key Features:**
- 🚀 Real-time API log analysis and anomaly detection
- 🤖 Unsupervised machine learning (Isolation Forest algorithm)
- 📊 Interactive React-based dashboard with WebSocket real-time updates
- 🔔 Automated email and webhook alerts
- 💾 Persistent SQLite-based alert history
- ⚙️ Dynamic threshold management
- 📈 Sensitivity analysis for robustness assessment
- 🐳 Docker container support

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip and npm package managers

### Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/kaoutar/mobile-api-misuse-detector.git
cd mobile-api-misuse-detector
```

#### Step 2: Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to project root
cd ..
```

#### Step 4: Database Setup
```bash
# Initialize SQLite database
python -c "from src.database import init_db; init_db()"
```

### Running the Application

#### Development Mode

**Terminal 1 - Backend (FastAPI):**
```bash
python main.py
# Server runs at http://localhost:8000
```

**Terminal 2 - Frontend (React):**
```bash
cd frontend
npm start
# Application opens at http://localhost:3000
```

#### Production Mode - Docker

```bash
# Build Docker image
docker build -t mobile-api-detector:latest .

# Run container
docker run -p 8000:8000 -p 3000:3000 \
  -e DATABASE_URL="sqlite:///./alerts.db" \
  mobile-api-detector:latest
```

## Usage

### 1. Upload API Logs

#### Via Web Interface
1. Open http://localhost:3000
2. Navigate to "Import Log"
3. Select a log file (JSON or text format)
4. Click "Upload and Analyze"

#### Via REST API
```bash
curl -X POST \
  -F "file=@your_logs.json" \
  http://localhost:8000/api/upload
```

### 2. Supported Log Formats

**JSON Format:**
```json
[
  {
    "timestamp": "2024-05-15T12:34:56Z",
    "source_ip": "192.168.1.100",
    "request_path": "/api/v1/login",
    "http_method": "POST",
    "http_status": 200,
    "user_agent": "MobileApp/1.0",
    "payload_size": 256,
    "response_time_ms": 125
  },
  ...
]
```

**Text/Nginx Format:**
```
192.168.1.100 - - [15/May/2024:12:34:56] "POST /api/v1/login HTTP/1.1" 200 256
```

### 3. View Results

Access the dashboard at http://localhost:3000 to:
- View detected anomalies in real-time
- Inspect individual alerts with forensic details
- Analyze anomaly scores over time
- Configure detection thresholds
- Export alert history as CSV

### 4. Configure Detection Settings

**Via REST API:**
```bash
# Get current settings
curl http://localhost:8000/api/settings

# Update threshold
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.75, "contamination": 0.01}'
```

### 5. Export Results

**CSV Export:**
```bash
curl http://localhost:8000/api/alerts/export \
  --output alerts.csv
```

## Algorithm Details

### Isolation Forest Anomaly Detection

The platform uses the Isolation Forest algorithm, which detects anomalies by isolating outliers in a random forest of binary trees.

**Anomaly Score Formula:**
```
s(x, n) = 2^(-E(h(x))/c(n))
```

Where:
- `E(h(x))` = average path length of sample x in the trees
- `c(n)` = average path length in a Binary Search Tree
- Scores close to 1 indicate anomalies
- Scores close to 0 indicate normal behavior

**Configuration:**
- `n_estimators`: 100 (number of trees)
- `contamination`: 0.01 (expected anomaly rate)
- `threshold`: Dynamic (adjusted based on score distribution)

### Feature Extraction

The system extracts 6 core dimensions from API logs:

| Feature | Description | Type |
|---------|-------------|------|
| Source IP | Geo-IP categorized | Categorical |
| Request Path | Entropy-analyzed for injection detection | Categorical |
| User Agent | Distinguishes legitimate SDKs vs. headless browsers | Categorical |
| Response Status | Aggregated into HTTP code families (2xx/3xx/4xx/5xx) | Categorical |
| Payload Size | Identifies data exfiltration | Numerical |
| Inter-Arrival Time | Time between sequential requests from same session | Numerical |

## Evaluation

### Datasets

**Synthetic Dataset:**
- 1,000,000 API calls
- 5% injected anomalies (brute-force, data scraping, injection attacks)
- Realistic traffic patterns

**Real-World Dataset:**
- 250,000 API calls
- Collected from production mobile application
- 7-day observation period

### Results

| Metric | Synthetic | Real-World |
|--------|-----------|-----------|
| Precision | 0.94 | 0.90 |
| Recall | 0.93 | 0.88 |
| F1-Score | 0.94 | 0.89 |
| Avg. Latency | 120 ms | 150 ms |

**Interpretation:**
- High precision (94%) indicates low false positive rate
- Strong recall (93%) ensures most anomalies are detected
- Sub-second latency suitable for real-time alerts
- Real-world performance slightly lower due to natural data complexity

## Architecture

### Three-Tier Design

```
┌─────────────────────────┐
│  Visualization Layer    │
│  (React Dashboard)      │
│  (WebSocket Real-time)  │
│  (SQLite Audit Trail)   │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  Analytical Core        │
│  (Feature Extraction)   │
│  (Isolation Forest)     │
│  (Background Tasks)     │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  Data Ingestion Layer   │
│  (FastAPI Gateway)      │
│  (Log Normalization)    │
│  (Async Processing)     │
└─────────────────────────┘
```

### Technology Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, scikit-learn
- **Frontend**: React 18+, TypeScript, Tailwind CSS, Recharts
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **ML**: scikit-learn 1.3+
- **DevOps**: Docker, Docker Compose

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=sqlite:///./alerts.db
# Or for PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/api_detector

# FastAPI
FASTAPI_ENV=development
FASTAPI_DEBUG=true
FASTAPI_WORKERS=4

# Alert Configuration
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_SERVER=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_FROM=noreply@example.com
ALERT_EMAIL_PASSWORD=your_password

WEBHOOK_URL=https://your-webhook-endpoint.com/alerts

# ML Configuration
ML_N_ESTIMATORS=100
ML_CONTAMINATION=0.01
ML_THRESHOLD=0.7

# Security
API_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
```

### Advanced Configuration

**config.yaml** (for threshold tuning):
```yaml
detection:
  algorithm: isolation_forest
  n_estimators: 100
  contamination: 0.01
  threshold_auto_adjust: true
  
features:
  - source_ip
  - request_path
  - user_agent
  - response_status
  - payload_size
  - inter_arrival_time

alerts:
  enabled: true
  email_recipients:
    - security-team@company.com
  slack_webhook: https://hooks.slack.com/...
  
logging:
  level: INFO
  file: logs/detector.log
```

## API Endpoints

### Upload and Analysis

**POST /api/upload**
```bash
curl -X POST -F "file=@logs.json" http://localhost:8000/api/upload
```

Response:
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "message": "Logs uploaded successfully"
}
```

### Get Alerts

**GET /api/alerts**
```bash
curl http://localhost:8000/api/alerts?limit=10&offset=0
```

### Get Alert Details

**GET /api/alerts/{alert_id}**
```bash
curl http://localhost:8000/api/alerts/550e8400-e29b-41d4-a716-446655440000
```

### Settings Management

**GET /api/settings**
```bash
curl http://localhost:8000/api/settings
```

**POST /api/settings**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"threshold": 0.75, "contamination": 0.01}' \
  http://localhost:8000/api/settings
```

### Export Results

**GET /api/alerts/export**
```bash
curl http://localhost:8000/api/alerts/export > alerts.csv
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_detection.py -v
```

### Integration Tests

```bash
# Test with sample dataset
python tests/integration_test.py --dataset data/sample_logs.json
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/alerts
```

## Data Privacy and Security

- ✅ Sensitive data (tokens, API keys) automatically redacted from logs during ingestion
- ✅ SQLite database protected via filesystem permissions
- ✅ Alert logs signed for non-repudiation
- ✅ API endpoints protected via Bearer token authentication
- ✅ HTTPS support for production deployments
- ✅ CORS restrictions configurable

## Limitations

1. **Temporal Modeling**: Isolation Forest doesn't capture sequence patterns; slow attacks spanning hours may be missed. Future versions will integrate LSTM-based detectors.

2. **Scalability**: SQLite limits throughput to ~10,000 requests/second. PostgreSQL or time-series databases (InfluxDB, TimescaleDB) recommended for production deployments handling millions of daily API calls.

3. **Integration**: Native connectors for Elastic, Splunk, and other SIEM platforms planned for v1.1+.

## Future Roadmap

- **v1.1 (Q3 2024)**:
  - PostgreSQL support
  - SIEM connectors (Elasticsearch, Splunk)
  - Explainable AI (SHAP integration)

- **v1.2 (Q4 2024)**:
  - LSTM-based temporal anomaly detection
  - Kubernetes deployment examples
  - Mobile SDK (Android/iOS)

- **v2.0 (2025)**:
  - Distributed architecture with Apache Kafka
  - Advanced fuzzy logic for uncertainty handling
  - Custom anomaly detection rules DSL

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use Mobile API Misuse Detector in your research, please cite:

```bibtex
@article{menacera2024mobile,
  title={Mobile API Misuse Detector: An Active-Security Platform for Detecting API Abuse in Mobile Applications},
  author={Menacera, Kaoutar and Laafar, Ayoub},
  journal={SoftwareX},
  year={2024},
  doi={10.1016/j.softx.2024.XXXXX},
  url={https://github.com/kaoutar/mobile-api-misuse-detector}
}
```

## Support

For issues, questions, or suggestions:
- 📧 Email: ayoub.laafar@ucd.ac.ma
- 🐛 GitHub Issues: https://github.com/kaoutar/mobile-api-misuse-detector/issues
- 📖 Documentation: https://github.com/kaoutar/mobile-api-misuse-detector/wiki

## Acknowledgments

- scikit-learn team for the Isolation Forest implementation
- FastAPI framework developers
- React community
- Security team at partner mobile application provider

---

**Current Version:** v1.0.0  
**Last Updated:** 2024-05-16  
**Status:** Production Ready ✅
