<div align="center">

<img src="https://img.shields.io/badge/Security-Platform-0A2342?style=for-the-badge&logoColor=white" />

# 🛡️ Mobile API Misuse Detector

**An enterprise-grade Active Security Platform for real-time API abuse detection in mobile environments,  
powered by unsupervised Machine Learning.**

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-0A2342?style=flat-square)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=React&logoColor=black)](https://reactjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)

<br/>

[📖 Documentation](#️-installation--setup) · [🚀 Features](#-key-features) · [📸 Screenshots](#-ui-showcase) · [📡 API](#-api-endpoints) · [📄 Research](#-academic-research)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#️-system-architecture)
- [Key Features](#-key-features)
- [Demo](#-demo)
- [UI Showcase](#-ui-showcase)
- [Installation & Setup](#️-installation--setup)
- [API Endpoints](#-api-endpoints)
- [Academic Research](#-academic-research)
- [Contributors](#-contributors)

---

## 🔍 Overview

The **Mobile API Misuse Detector** is a production-ready security platform that identifies and mitigates API abuse patterns in real time. By leveraging unsupervised anomaly detection, it requires no predefined attack signatures — making it effective against zero-day threats and novel attack vectors targeting mobile APIs.

> **Built for DevSecOps teams** who need continuous, intelligent monitoring without the overhead of rule-based systems.

---

## 🏗️ System Architecture

The platform uses a modern, decoupled architecture engineered for low-latency analysis and real-time response.

```mermaid
graph TD
    A[📱 Mobile App / Client] -->|JSON Logs| B[⚡ FastAPI Backend]
    B -->|Async Task| C[🤖 Isolation Forest Engine]
    C -->|Store Results| D[(🗄️ SQLite Database)]
    B -->|WebSocket| E[📊 React Dashboard]
    D -->|Audit Logs| E
    C -->|Trigger| F[📧 Email Alerts]

    style A fill:#0A2342,color:#fff
    style B fill:#009688,color:#fff
    style C fill:#F7931E,color:#fff
    style D fill:#444,color:#fff
    style E fill:#61DAFB,color:#000
    style F fill:#E53E3E,color:#fff
```

### Core Components

| Component | Technology | Role |
|-----------|-----------|------|
| **API Backend** | FastAPI (Python) | Async log ingestion & ML inference |
| **Detection Engine** | Isolation Forest (Scikit-Learn) | Zero-day anomaly detection |
| **Frontend Dashboard** | React + WebSocket | Real-time monitoring UI |
| **Persistent Storage** | SQLite | Audit trails & alert history |
| **Notification System** | SMTP / Webhooks | Automated threat alerting |

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

**🚀 Real-time Log Ingestion**  
Supports Nginx, Express, and Spring log formats with drag-and-drop upload.

**🤖 AI-Powered Detection**  
Unsupervised anomaly detection using `IsolationForest` — no labeled data required.

**📊 Behavioral Clustering**  
Groups suspicious IPs by attack pattern: Bruteforce, Scrapers, Traffic Spikes.

</td>
<td width="50%">

**🔔 Active Alerting**  
Automated Email & Webhook notifications triggered by background tasks.

**⚙️ Dynamic Thresholds**  
Adjust detection sensitivity on-the-fly via the admin dashboard.

**📜 Full Audit Trail**  
Complete persistence of every alert, event, and system configuration change.

</td>
</tr>
</table>

---

## 🎬 Demo

> **📹 Video walkthrough coming soon.**  
> A full demonstration of the platform — from log ingestion to anomaly detection and alerting — will be available here.

<!--
TO ADD YOUR VIDEO later:

Option 1 - YouTube thumbnail (recommended):
[![Watch the demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

Option 2 - Direct video file hosted on GitHub:
https://github.com/Ayoublaa/mobile/assets/YOUR_ASSET_ID/your-demo.mp4
-->

<div align="center">

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              🎬  Demo Video                         │
│                                                     │
│         [ Coming Soon — Link to be added ]          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

</div>

---

## 📸 UI Showcase

### Dashboard Overview
> Real-time visibility of system health and active threats.

<img src="scrennshot/dashboard.png" width="100%" alt="Dashboard Overview" />

<br/>

### Anomaly Analytics
> Visualizing anomaly scores, patterns, and behavioral clusters.

<img src="scrennshot/graphs.png" width="100%" alt="Anomaly Analytics" />

<br/>

<table>
<tr>
<td width="50%" align="center">

**📥 Log Ingestion**  
*Seamless drag-and-drop log analysis*

<img src="scrennshot/importlog.png" width="100%" alt="Log Ingestion" />

</td>
<td width="50%" align="center">

**📋 Alert Journal**  
*Complete history of security incidents*

<img src="scrennshot/jouranldaletre.png" width="100%" alt="Alert Journal" />

</td>
</tr>
<tr>
<td width="50%" align="center">

**📧 Email Notifications**  
*Immediate alerts for critical threats*

<img src="scrennshot/email.png" width="100%" alt="Email Notifications" />

</td>
<td width="50%" align="center">

**🛡️ Security Recommendations**  
*Actionable AI-driven mitigation steps*

<img src="scrennshot/recommendation.png" width="100%" alt="Security Recommendations" />

</td>
</tr>
</table>

---

## 🛠️ Installation & Setup

### Prerequisites

- Python **3.9+**
- Node.js **18+**
- An SMTP server (e.g., Gmail) for email alerts

### 1. Clone the Repository

```bash
git clone https://github.com/Ayoublaa/mobile.git
cd mobile
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Configuration

Create a `.env` file at the **project root**:

```env
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=admin@example.com
```

> ⚠️ **Never commit your `.env` file.** Make sure it is listed in `.gitignore`.

### 5. Run the Application

**Start the backend:**
```bash
uvicorn backend.main:app --reload
```

**Start the frontend** (in a new terminal):
```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-log` | Ingest and analyze a log file |
| `GET` | `/stats` | Retrieve enriched metrics for the dashboard |
| `GET` | `/alerts/history` | Access the persistent security audit trail |
| `POST` | `/settings` | Configure alert thresholds and system state |

Full interactive API documentation available at `http://localhost:8000/docs` (Swagger UI).

---

## 📄 Academic Research

This platform is the subject of a comprehensive academic security study. A **14-page scientific paper** following the **SoftwareX (Elsevier)** template is included in this repository.

```
📁 report.tex   ← Full LaTeX source (SoftwareX format)
```

Topics covered: anomaly detection methodology, feature engineering, evaluation metrics, and comparative analysis against signature-based systems.

---

## 👥 Contributors

<table>
<tr>
<td align="center">
<b>Kaoutar Menacera</b>
</td>
<td align="center">
<b>Ayoub Laafar</b>
</td>
</tr>
</table>

---

<div align="center">

**Built with 

https://github.com/user-attachments/assets/a0ef8412-9516-44cb-a6cd-862d3c5fb53d





for the DevSecOps Community**

*If this project helped you, consider giving it a ⭐*

</div>
