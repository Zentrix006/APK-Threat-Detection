# 🛡️ APK Threat Intelligence Platform

<h1 align="center">🛡️ APK Threat Intelligence Platform</h1>
<h3 align="center">AI-Powered Android Malware Analysis • Threat Intelligence • Dynamic Analysis</h3>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com/?lines=Android+Malware+Analysis+Platform;Static+%26+Dynamic+Analysis;Threat+Intelligence+Correlation;MITRE+ATT%26CK+Mapping;AI-Powered+Threat+Investigations&center=true&width=800&height=45&color=58A6FF&vCenter=true" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Android-success?style=flat-square" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/Next.js-Frontend-black?style=flat-square&logo=nextdotjs" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/Redis-Cache-red?style=flat-square&logo=redis" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

```bash
$ whoami

🛡️ APK Threat Intelligence Platform
🔍 Android Malware Analysis & Threat Investigation Framework
⚡ Static + Dynamic Analysis + Threat Correlation
🤖 AI-Powered Investigation Reports
📊 MITRE ATT&CK Mapping & Risk Scoring
```

---

## 🚀 Core Features

```bash
$ ls /features

📦 APK Analysis
▸ Upload and reverse engineer APK files
▸ Static analysis with MobSF, JADX, APKTool, Androguard
▸ Extract URLs, IPs, Domains & Indicators of Compromise

📱 Dynamic Analysis
▸ Android Emulator Sandbox
▸ Frida Runtime Instrumentation
▸ ADB Integration
▸ Network Traffic Monitoring
▸ C2 Communication Detection

🕸️ Threat Intelligence
▸ IOC Correlation Engine
▸ Threat Graph Visualization
▸ MITRE ATT&CK Mapping
▸ Malware Family Classification

🤖 AI Investigation
▸ Ollama + Qwen3 Integration
▸ Explainable Threat Reports
▸ Automated Analyst Summaries
▸ PDF Report Generation

📊 Risk Assessment
▸ XGBoost Risk Scoring
▸ Behavioral Analysis
▸ Threat Prioritization
```

##📸 Screenshots

<img width="1360" height="603" alt="Screenshot 2026-06-11 042645" src="https://github.com/user-attachments/assets/74595d94-685b-47c9-8c13-e0eb70feb22c" />
<img width="1024" height="485" alt="image" src="https://github.com/user-attachments/assets/69305060-46d6-4211-80c1-25a924d6c1ab" />
<img width="1025" height="457" alt="image" src="https://github.com/user-attachments/assets/2ea6dc3e-ca8d-459e-b84d-6b70c6881ce2" />
<img width="1066" height="763" alt="image" src="https://github.com/user-attachments/assets/6501e0e3-1e8d-4b1e-863c-3b17878926e8" />
<img width="1018" height="365" alt="image" src="https://github.com/user-attachments/assets/2f5bfc63-b96a-46a5-98d1-65d0198dcef2" />
<img width="1019" height="378" alt="image" src="https://github.com/user-attachments/assets/181a09b4-00ca-4d84-9b2a-c6ac338876b4" />
<img width="1013" height="456" alt="image" src="https://github.com/user-attachments/assets/1e5232a0-2c42-43bc-9cda-3141bf8822c9" />
<img width="649" height="664" alt="image" src="https://github.com/user-attachments/assets/e6df060c-7569-4a2e-b3b7-72d98ba27045" />

---

## 🏗️ Architecture

```bash
$ cat architecture.txt

┌─────────────┐
│   Next.js   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Nginx    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FastAPI   │
└──────┬──────┘
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
Redis PostgreSQL Analysis
 Cache Database Engines

       │
 ┌─────┼─────┐
 ▼     ▼     ▼
Static Dynamic AI/ML
```

---

## ⚙️ Technology Stack

```bash
$ tech-stack

🌐 Frontend
▸ Next.js 14
▸ Tailwind CSS
▸ ShadCN UI
▸ Recharts

⚡ Backend
▸ FastAPI
▸ SQLAlchemy
▸ Pydantic

🛡️ Analysis Tools
▸ MobSF
▸ APKTool
▸ JADX
▸ Androguard
▸ Frida
▸ ADB

🤖 AI / ML
▸ Ollama
▸ Qwen3
▸ XGBoost

🗄️ Infrastructure
▸ PostgreSQL
▸ Redis
▸ Docker
▸ Nginx
▸ Ubuntu
```

---

## 🔬 Analysis Pipeline

```bash
$ run-analysis

[1] Upload APK
      │
      ▼
[2] Static Analysis
      │
      ▼
[3] Dynamic Execution
      │
      ▼
[4] IOC Extraction
      │
      ▼
[5] Threat Correlation
      │
      ▼
[6] Risk Scoring
      │
      ▼
[7] MITRE ATT&CK Mapping
      │
      ▼
[8] AI Investigation Report
      │
      ▼
[9] Threat Graph Generation
      │
      ▼
[10] PDF Export
```

---

## 📁 Project Structure

```bash
$ tree apk-threat-intelligence

apk-threat-intelligence/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
│
├── backend/
│   ├── api/
│   ├── analysis/
│   ├── ai/
│   ├── ml/
│   ├── reporting/
│   ├── db/
│   └── main.py
│
├── docker/
├── docs/
├── screenshots/
└── README.md
```

---

## 🚀 Quick Start

```bash
$ git clone https://github.com/Zentrix006/APK-Threat-Detection.git

$ cd APK-Threat-Detection

$ docker-compose up -d
```

### Services

```bash
Frontend  : http://localhost:3000
Backend   : http://localhost:8000
Swagger   : http://localhost:8000/docs
PostgreSQL: localhost:5432
Redis     : localhost:6379
```

---

## 📡 API Overview

```bash
$ curl api/v1

POST   /apks/upload
GET    /apks/{id}
GET    /apks/{id}/analysis

POST   /analysis/static
POST   /analysis/dynamic

GET    /threats/graph/{id}
GET    /threats/c2-detection
GET    /threats/mitre-mapping

GET    /reports/{id}
```

---

## 🛡️ Security Capabilities

```bash
$ capabilities

🔍 Malware Behavior Analysis
🌐 IOC Extraction & Correlation
📡 Network Traffic Monitoring
🎯 MITRE ATT&CK Mapping
📊 Risk Scoring Engine
🕵️ C2 Detection
📑 Automated Reporting
🤖 AI-Powered Investigations
```
## 🎯 Future Roadmap

```bash
$ roadmap

[ ] VirusTotal Integration
[ ] Shodan Intelligence Enrichment
[ ] YARA Rule Engine
[ ] Multi-APK Correlation
[ ] Threat Hunting Dashboard
[ ] Real Device Dynamic Analysis
[ ] SIEM Integration
[ ] Kubernetes Production Deployment
```

---

## 🤝 Contributing

```bash
$ contribute

1. Fork Repository
2. Create Feature Branch
3. Commit Changes
4. Push Changes
5. Open Pull Request
```

---

## 🏆 Acknowledgements

```bash
$ credits

▸ MobSF Team
▸ Frida Project
▸ JADX Team
▸ Androguard Contributors
▸ MITRE ATT&CK Framework
▸ Open Source Security Community
```

---

## 📜 License

```bash
$ cat LICENSE

MIT License
```

---

<p align="center">
  <b>🛡️ Analyzing APKs • Correlating Threats • Building Intelligence</b>
</p>

<p align="center">
  Made with ☕, Linux, and Threat Hunting
</p>
