# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- 8GB RAM minimum
- 10GB disk space

## Local Development Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd apk-threat-detection
```

### 2. Create environment file
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DB_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
JWT_SECRET=your_jwt_secret
OLLAMA_MODEL=qwen3
```

### 3. Start all services
```bash
docker-compose up -d
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

### 4. Verify services are running
```bash
docker-compose ps
```

### 5. Check logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Manual Installation (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/apk_threat"
export REDIS_URL="redis://localhost:6379/0"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Setup

```bash
# Install PostgreSQL
# Create database
createdb apk_threat

# Create user
createuser apk_user
psql -d apk_threat -c "ALTER USER apk_user WITH PASSWORD 'password';"

# Apply schema
psql -d apk_threat < ../docker/init-db.sql
```

### Redis Setup

```bash
# Start Redis
redis-server
```

## Usage

### 1. Upload APK
- Go to http://localhost:3000
- Click "Upload APK"
- Select your APK file
- Wait for upload to complete

### 2. Run Analysis
- Navigate to the uploaded APK
- Click "Run Static Analysis" for code analysis
- Click "Run Dynamic Analysis" for runtime behavior (requires Android emulator)

### 3. View Results
- See risk score and threat classification
- Review detected indicators
- Check MITRE ATT&CK mappings

### 4. Generate Report
- Click "Generate Report"
- AI will analyze and generate a threat intelligence report
- Download as PDF

## API Examples

### Upload APK
```bash
curl -X POST http://localhost:8000/api/v1/apks/upload \
  -F "file=@path/to/app.apk"
```

### Get APK Info
```bash
curl http://localhost:8000/api/v1/apks/{apk_id}
```

### Run Static Analysis
```bash
curl -X POST http://localhost:8000/api/v1/analysis/static/{apk_id}
```

### Get Risk Score
```bash
curl http://localhost:8000/api/v1/analysis/{apk_id}/risk-score
```

### Generate Report
```bash
curl -X POST http://localhost:8000/api/v1/reports/generate/{apk_id}
```

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Check Redis is running
- Verify database credentials in .env

### Frontend connection errors
- Ensure backend is running at http://localhost:8000
- Check NEXT_PUBLIC_API_URL in .env

### Analysis tools not found
- Verify APKTool, JADX, Androguard are installed
- Check paths in .env

### Ollama not responding
- Ensure Ollama container is running
- Run: `docker-compose logs ollama`
- Pull model: `ollama pull qwen3`

## Performance Tuning

### Increase worker processes
Edit docker-compose.yml:
```yaml
backend:
  environment:
    WORKERS: 8
```

### Increase database connections
Edit docker-compose.yml:
```yaml
postgres:
  environment:
    POSTGRES_INIT_ARGS: -c max_connections=200
```

### Enable caching
Configure Redis in .env for better performance

## Security Recommendations

1. **Change default passwords** in .env
2. **Enable HTTPS** with SSL certificates
3. **Use strong JWT secrets**
4. **Configure firewall** to restrict port access
5. **Keep dependencies updated**
6. **Enable authentication** for API access
7. **Use environment-specific configs**

## Next Steps

- Read [API.md](./API.md) for detailed API documentation
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Review [ANALYSIS_PIPELINE.md](./ANALYSIS_PIPELINE.md) for analysis workflow

## Support

For issues and questions:
- Check Docker logs: `docker-compose logs -f`
- Review API documentation: http://localhost:8000/docs
- Check GitHub issues: [repository/issues]
