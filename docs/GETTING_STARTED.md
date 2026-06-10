# APK Threat Intelligence Platform - Getting Started

This comprehensive guide will help you get the APK Threat Intelligence Platform up and running.

## 🚀 Quick Start (5 minutes)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Navigate to project directory
cd apk-threat-detection

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Access the platform
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## 📋 System Requirements

- **OS**: Ubuntu 20.04+ / macOS / Windows 10+
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 10GB minimum
- **Docker**: 20.10+ (if using Docker)
- **Node.js**: 18.0+ (for frontend development)
- **Python**: 3.11+ (for backend development)

## 🔧 Configuration

### Environment Variables

Create `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://apk_user:apk_password@localhost:5432/apk_threat
REDIS_URL=redis://:redis_password@localhost:6379/0

# Security
JWT_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Analysis Tools
ANDROID_SDK_PATH=/opt/android-sdk
FRIDA_VERSION=latest

# AI/ML
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

See `.env.example` for all available options.

## 📊 First Steps

### 1. Upload an APK

1. Go to http://localhost:3000
2. Click **"Upload APK"** in the sidebar
3. Select an Android APK file (max 500MB)
4. Wait for upload to complete

### 2. Run Analysis

1. Click **"Dashboard"** to view uploaded APKs
2. Click **"View"** on an APK to open its details
3. Click **"Run Static Analysis"** to analyze the APK
   - Extracts permissions, APIs, URLs, etc.
   - Calculates risk score
   - Takes ~1-3 minutes
4. (Optional) Click **"Run Dynamic Analysis"** to monitor runtime behavior
   - Requires Android emulator
   - Takes ~5-15 minutes
   - Records network traffic and API calls

### 3. View Results

1. See the **Risk Score** (0-100) and risk level
2. Review detected **Malware Classifications**
3. Check **Indicators** (permissions, URLs, IPs, etc.)
4. Click **"Generate Report"** for an AI-powered analysis report

### 4. Download Report

1. Click **"Generate Report"** (or select existing report)
2. Click **"Download"** when ready
3. Open PDF report with detected threats and recommendations

## 🏗️ Architecture Overview

```
Frontend (Next.js/React)
    ↓ (HTTP/REST)
Nginx Gateway (Reverse Proxy)
    ↓
Backend (FastAPI)
    ↓
┌─────┬───────┬──────────┬──────────┐
│ DB  │ Cache │ Storage  │ Analysis │
└─────┴───────┴──────────┴──────────┘
```

## 📁 Project Structure

```
apk-threat-detection/
├── frontend/                 # Next.js web application
│   ├── src/app/             # Pages and layout
│   ├── src/components/      # React components
│   └── public/              # Static assets
│
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── analysis/       # Analysis engines
│   │   ├── ml/             # ML models
│   │   ├── ai/             # AI integrations
│   │   ├── db/             # Database
│   │   └── main.py         # App entry point
│   └── requirements.txt
│
├── docker/                  # Docker configuration
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── init-db.sql
│
├── docs/                    # Documentation
│   ├── SETUP.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── ANALYSIS_PIPELINE.md
│
└── .env.example            # Environment template
```

## 🔍 Key Features

### ✅ Implemented
- APK upload and storage
- Manifest analysis
- Permission extraction
- Suspicious API detection
- Network indicator extraction
- Risk scoring with fallback heuristic
- Malware classification
- MITRE ATT&CK mapping
- PDF report generation with ReportLab
- Interactive dashboard
- REST API

### 🚧 In Development
- Dynamic analysis with Android emulator
- Frida instrumentation
- Network traffic analysis
- Advanced ML models
- Real-time WebSocket updates
- Multi-user authentication

### 🔮 Planned Features
- Threat graph visualization
- C2 detection and tracking
- Ensemble ML models
- Integration with threat feeds
- Mobile app (React Native)
- Kubernetes deployment
- GraphQL API

## 🐛 Troubleshooting

### Docker Issues

**Problem**: "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker
sudo systemctl start docker
# or on macOS
open --application Docker
```

**Problem**: "Port already in use"
```bash
# Solution: Use different ports in docker-compose.yml
# Or kill process using the port
lsof -i :8000
kill -9 <PID>
```

### Backend Issues

**Problem**: "ModuleNotFoundError"
```bash
# Solution: Ensure venv is activated and requirements installed
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: "Database connection error"
```bash
# Solution: Check PostgreSQL is running
psql -U apk_user -d apk_threat
# or with Docker
docker-compose exec postgres psql -U apk_user -d apk_threat
```

### Frontend Issues

**Problem**: "Cannot find module"
```bash
# Solution: Install dependencies
npm install
# or clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem**: "API connection error"
```bash
# Solution: Check backend is running and .env is correct
# Verify: http://localhost:8000/health returns OK
# Check NEXT_PUBLIC_API_URL in .env
```

## 📚 Documentation

- [Full Setup Guide](./docs/SETUP.md) - Detailed installation steps
- [API Reference](./docs/API.md) - Complete API documentation
- [System Architecture](./docs/ARCHITECTURE.md) - Technical architecture
- [Analysis Pipeline](./docs/ANALYSIS_PIPELINE.md) - How analysis works

## 🚀 Deployment

### Docker Compose (Development/Small Deployments)
```bash
docker-compose up -d
```

### Ubuntu Manual Deployment
See [docs/SETUP.md](./docs/SETUP.md) for step-by-step instructions

### Production Checklist
- [ ] Change all default passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall
- [ ] Set up monitoring and logging
- [ ] Enable automated backups
- [ ] Configure rate limiting
- [ ] Review security headers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support & Issues

- **Documentation**: [./docs](./docs)
- **API Docs**: http://localhost:8000/docs (when running)
- **GitHub Issues**: [Report bugs here]

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)

## ⚙️ Advanced Configuration

### Enable HTTPS

1. Obtain SSL certificate (Let's Encrypt):
```bash
sudo certbot certonly --standalone -d yourdomain.com
```

2. Update `docker/nginx.conf` and mount certificates

3. Restart Nginx:
```bash
docker-compose restart nginx
```

### Scale Backend Services

1. Increase workers in `docker-compose.yml`:
```yaml
backend:
  environment:
    WORKERS: 8
```

2. Restart backend:
```bash
docker-compose restart backend
```

### Monitor Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Filter by keyword
docker-compose logs -f backend | grep ERROR
```

## 🎯 Next Steps

1. **Explore the Dashboard**: Get familiar with the UI
2. **Read API Docs**: Understanding the REST API
3. **Try Analysis**: Upload a test APK and run analysis
4. **Review Reports**: See generated threat reports
5. **Customize**: Modify for your use cases
6. **Deploy**: Set up for production use

---

**Happy Threat Hunting! 🛡️**

For more information, visit the [documentation](./docs).
