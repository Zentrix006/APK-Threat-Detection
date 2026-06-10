# APK Threat Intelligence Platform

A comprehensive platform for analyzing Android APK files, detecting threats, and generating AI-powered threat intelligence reports.

## Features

✅ **APK Analysis**
- Upload and reverse engineer APK files
- Static analysis using MobSF, APKTool, JADX, Androguard
- Extract URLs, IPs, and suspicious domains

✅ **Dynamic Analysis**
- Android Emulator integration
- Frida instrumentation framework
- ADB device communication
- Network traffic capture (tcpdump)
- C2 communication detection

✅ **Threat Intelligence**
- Automated risk scoring with XGBoost
- MITRE ATT&CK framework mapping
- Threat graph visualization (APK ↔ IP ↔ Domain)
- ML-based malware classification

✅ **AI-Powered Reporting**
- Ollama + Qwen3 LLM integration
- Auto-generated investigation reports
- ReportLab PDF generation

✅ **Database**
- PostgreSQL for persistent storage
- Redis for caching and queue management

## Tech Stack

### Frontend
- Next.js 14
- Tailwind CSS
- ShadCN Components
- Recharts for visualization

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- Pydantic validation

### Analysis Tools
- MobSF - Mobile Security Framework
- APKTool - APK decompilation
- JADX - Java decompiler
- Androguard - APK analysis

### ML/AI
- XGBoost - Risk scoring
- Ollama + Qwen3 - Report generation

### Deployment
- Docker & Docker Compose
- Ubuntu 22.04
- Nginx reverse proxy
- PostgreSQL 15
- Redis 7

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 8GB RAM minimum

### Local Development

```bash
# Clone the repository
git clone <repo>
cd apk-threat-detection

# Start all services
docker-compose up -d

# Backend at: http://localhost:8000
# Frontend at: http://localhost:3000
# API docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### APK Management
- `POST /api/v1/apks/upload` - Upload APK
- `GET /api/v1/apks/{apk_id}` - Get APK details
- `GET /api/v1/apks/{apk_id}/analysis` - Get analysis results

### Analysis
- `POST /api/v1/analysis/static` - Run static analysis
- `POST /api/v1/analysis/dynamic` - Run dynamic analysis
- `GET /api/v1/analysis/{analysis_id}/report` - Generate report

### Threat Intelligence
- `GET /api/v1/threats/graph/{apk_id}` - Threat graph
- `GET /api/v1/threats/c2-detection` - C2 detection results
- `GET /api/v1/threats/mitre-mapping` - MITRE ATT&CK mapping

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│              Tailwind + ShadCN + Recharts               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (Nginx)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Routes: APKs, Analysis, Reports, Threats         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────┬─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌────────┐ ┌──────┐ ┌─────────┐ ┌──────────┐
│  APK   │ │Redis │ │PostgreSQL │ │ Analysis │
│Storage │ │Cache │ │Database   │ │ Tools    │
└────────┘ └──────┘ └─────────┘ └──────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    ┌────────┐   ┌─────────┐   ┌──────────┐
    │ Static │   │ Dynamic │   │ML/AI     │
    │Analysis│   │Analysis │   │Analysis  │
    └────────┘   └─────────┘   └──────────┘
```

## Project Structure

```
apk-threat-detection/
├── frontend/               # Next.js application
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/              # Utilities
│   └── public/           # Static assets
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── analysis/     # Analysis engines
│   │   ├── ml/           # ML models
│   │   ├── ai/           # AI integrations
│   │   ├── reporting/    # Report generation
│   │   ├── db/           # Database models
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker/               # Docker configurations
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.example
│
└── docs/                 # Documentation
    ├── API.md
    ├── SETUP.md
    ├── ARCHITECTURE.md
    └── ANALYSIS_PIPELINE.md
```

## Configuration

See `.env.example` for environment variables:

```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/apk_threat
REDIS_URL=redis://redis:6379/0

# API Keys
VIRUSTOTAL_API_KEY=
SHODAN_API_KEY=

# Analysis
ANDROID_SDK_PATH=/opt/android-sdk
FRIDA_SERVER_PORT=27042

# AI/ML
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=qwen3

# Security
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

## Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Lint
flake8 app/
black app/

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
npm start

# Lint and format
npm run lint
npm run format
```

## Database Setup

PostgreSQL migrations are automatically handled with Alembic:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Docker Compose (Recommended for Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
See `docs/DEPLOYMENT_K8S.md` for Kubernetes manifests.

### Manual Ubuntu Deployment
See `docs/DEPLOYMENT_UBUNTU.md` for detailed setup instructions.

## Analysis Pipeline

1. **Upload** - User uploads APK file
2. **Storage** - APK stored in PostgreSQL with metadata
3. **Static Analysis** - MobSF/JADX/Androguard extract metadata
4. **Dynamic Analysis** - Emulator executes APK with Frida instrumentation
5. **Threat Detection** - Extract IPs, URLs, C2 communications
6. **ML Scoring** - XGBoost calculates risk score
7. **MITRE Mapping** - Map techniques to MITRE ATT&CK
8. **AI Report** - Ollama/Qwen3 generates narrative report
9. **Visualization** - Build threat graph (APK ↔ IP ↔ Domain)
10. **Export** - Generate PDF report with ReportLab

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

- 📖 [Documentation](./docs)
- 🐛 [Report Issues](https://github.com/issues)
- 💬 [Discussions](https://github.com/discussions)

## Acknowledgments

- MobSF Team for Mobile Security Framework
- JADX for Java decompiler
- Frida team for dynamic instrumentation
- The security research community
