# Mobile API Misuse Detector

## Overview
This open‑source project provides a **real‑time active‑security platform** for detecting abuse of mobile backend APIs. It combines:
- FastAPI backend with asynchronous processing
- Isolation‑Forest unsupervised anomaly detection
- A premium React dashboard with glass‑morphism UI
- Persistent SQLite storage for logs, alerts and configurable settings

The system can ingest Nginx, Express or Spring logs, automatically flag spikes, bruteforce attempts, endpoint enumeration and more.

## Screenshots
Below are the key UI screens and diagrams that illustrate the architecture and workflow of the detector:

![Architecture diagram](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/architecture.png)

![Workflow diagram](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/workflow.png)

![Dashboard view](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/dashboard.png)

![Email alert template](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/email.png)

![Anomaly graphs](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/graphs.png)

![Log import screen](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/importlog.png)

![Journal of persisted alerts](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/jouranldaletre.png)

![Recommendation panel](file:///c:/Users/Windows/Desktop/mobile-api-misuse-detector/figures/recommendation.png)

## Quick start
```bash
# Clone the repo (once pushed)
# git clone https://github.com/Ayoublaa/mobile.git

# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

## Configuration (environment variables)
| Variable | Description |
|----------|-------------|
| `SMTP_USERNAME` | Email account for alerts |
| `SMTP_PASSWORD` | Password / app‑specific token |
| `EMAIL_FROM` | Sender address |
| `EMAIL_TO` | Comma‑separated list of recipients |
| `SMTP_HOST` | SMTP server (default: smtp.gmail.com) |
| `SMTP_PORT` | Port (default: 587) |

## License
MIT – see `LICENSE` for details.
