# System Architecture

## Overview

The APK Threat Intelligence Platform is a distributed system designed for comprehensive mobile malware analysis and threat detection.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Web Frontend (Next.js + React)                  │  │
│  │  - Dashboard & Analytics                        │  │
│  │  - APK Upload & Management                      │  │
│  │  - Analysis Results & Reports                   │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────────────────┘
                   │ HTTP/HTTPS
┌──────────────────▼───────────────────────────────────────┐
│              API Gateway (Nginx)                         │
│  - Request routing & load balancing                     │
│  - SSL/TLS termination                                  │
│  - Rate limiting & DDoS protection                      │
│  - Request logging & monitoring                         │
└──────────────────┬───────────────────────────────────────┘
                   │ gRPC/HTTP
┌──────────────────▼───────────────────────────────────────┐
│            Application Server Layer                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI Application                             │  │
│  │  ┌────────────┐  ┌──────────┐  ┌─────────────┐  │  │
│  │  │  APK Routes│  │Analysis  │  │  Reports    │  │  │
│  │  │  Management│  │  Routes  │  │  Routes     │  │  │
│  │  └────────────┘  └──────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────────────────┘
       ┌───────────┼───────────┬────────────┐
       │           │           │            │
       ▼           ▼           ▼            ▼
   ┌────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
   │Database│ │Cache │ │Storage   │ │Analysis  │
   │Handler │ │Layer │ │Service   │ │Services  │
   └────────┘ └──────┘ └──────────┘ └──────────┘
       │           │           │            │
       ▼           ▼           ▼            ▼
   PostgreSQL  Redis    File System  Analysis Engines
                          (APK files)
```

## Core Components

### 1. Frontend Layer

**Technology**: Next.js 14 + React 18 + Tailwind CSS

**Responsibilities**:
- User interface for APK upload and management
- Real-time dashboard and analytics
- Interactive threat visualization
- Report viewing and generation

**Key Features**:
- Server-side rendering (SSR) for performance
- Client-side state management with Zustand
- Responsive design with Tailwind CSS
- Component library with ShadCN UI

### 2. API Gateway

**Technology**: Nginx

**Responsibilities**:
- Request routing to microservices
- SSL/TLS termination
- Rate limiting and authentication
- Load balancing
- Request logging and monitoring

**Configuration**:
- HTTP to HTTPS redirect
- Security headers
- CORS handling
- Reverse proxy to backend services

### 3. Application Server

**Technology**: FastAPI (Python)

**Responsibilities**:
- HTTP API server
- Request validation
- Business logic orchestration
- Background task management
- Service coordination

**Key Modules**:
- **API Routes**: APK management, analysis, reports
- **Analysis Engine**: Static and dynamic APK analysis
- **ML/AI**: Risk scoring and threat classification
- **Reporting**: Report generation and export

### 4. Analysis Engines

#### Static Analysis
- **MobSF**: Extracts APK metadata and manifest information
- **APKTool**: Decompiles and disassembles APK files
- **JADX**: Java decompiler for source code analysis
- **Androguard**: In-depth APK analysis and feature extraction

**Processes**:
1. APK extraction
2. Manifest parsing
3. Permission analysis
4. Suspicious API detection
5. String extraction (URLs, IPs, domains)
6. Intent filter analysis

#### Dynamic Analysis
- **Android Emulator**: Executes APK in controlled environment
- **Frida**: Runtime instrumentation for API call monitoring
- **ADB**: Android Device Bridge for device communication
- **tcpdump**: Network traffic capture

**Processes**:
1. APK installation
2. App launch with monitoring
3. Runtime behavior capture
4. Network traffic analysis
5. File system monitoring
6. API call tracking

### 5. Machine Learning Pipeline

**Technology**: XGBoost + Scikit-learn

**Components**:
- **Feature Extraction**: 12+ features from analysis data
- **Risk Scorer**: Predicts malware probability
- **Classifier**: Categorizes malware families
- **Model Training**: Periodic retraining with new data

**Features Used**:
- Permission count
- Network connections
- Suspicious API usage
- C2 indicators
- Encryption/obfuscation patterns
- Intent filter analysis

### 6. AI Integration

**Technology**: Ollama + Qwen3 LLM

**Capabilities**:
- Natural language threat analysis
- Report generation
- Behavior explanation
- Recommendation synthesis

**Process**:
1. Context preparation from analysis results
2. LLM inference with Ollama
3. Report formatting and export
4. PDF generation with ReportLab

### 7. Data Storage

#### PostgreSQL (Primary Database)
- **Tables**:
  - `apk_files`: Uploaded APK metadata
  - `analyses`: Analysis execution records
  - `artifacts`: Extracted indicators (URLs, IPs, etc.)
  - `threats`: Detected threats and classifications
  - `reports`: Generated reports
  - `users`: User accounts and authentication
  - `ml_models`: Trained models and metrics

- **Features**:
  - ACID compliance
  - Full-text search
  - JSON support
  - Automatic backups

#### Redis (Cache & Queue)
- **Purpose**:
  - Session management
  - Analysis task queue
  - Rate limit tracking
  - Temporary data caching

- **TTL Management**:
  - Cache entries expire automatically
  - Queue items processed by workers

### 8. Background Processing

**Task Queue**: Celery/RQ

**Jobs**:
- Static APK analysis
- Dynamic APK execution
- Report generation
- ML model training
- Cleanup and maintenance

**Features**:
- Asynchronous execution
- Retry mechanism
- Priority queuing
- Result persistence

## Data Flow

### APK Analysis Pipeline

```
1. Upload (Frontend)
   └─> Store file (Backend)
       └─> Extract metadata (MobSF)
           └─> Decompile (APKTool/JADX)
               └─> Parse manifest
                   └─> Extract permissions, URLs, IPs
                       └─> Analyze APIs
                           └─> Calculate risk score (ML)
                               └─> Map MITRE ATT&CK
                                   └─> Generate report (AI)
                                       └─> Export PDF
```

### Real-time Updates

- WebSocket connections for live progress updates
- Server-Sent Events (SSE) for background task status
- Polling fallback for compatibility

## Security Architecture

### Authentication & Authorization
- JWT tokens for API access
- Role-based access control (RBAC)
- Token expiration and refresh
- Rate limiting per user

### Data Protection
- AES-256 encryption for sensitive data
- TLS 1.2+ for network communication
- Secure password hashing (bcrypt)
- HTTPS enforcement

### Network Security
- Firewall rules (Ubuntu iptables)
- DDoS protection (Nginx rate limiting)
- CORS configuration
- Security headers (X-Frame-Options, CSP, etc.)

## Scalability Considerations

### Horizontal Scaling

**Frontend**:
- Multiple Node.js instances behind Nginx
- Static asset caching with CDN
- Database connection pooling

**Backend**:
- Multiple FastAPI workers
- Celery task distribution
- Redis cluster for cache
- PostgreSQL replication

### Performance Optimization

- Response compression (gzip)
- Database query optimization
- Caching strategies (browser, server, database)
- Asynchronous I/O operations
- Connection pooling

## Deployment Topology

### Development
- Single machine Docker Compose
- All services in containers
- Shared volumes for development

### Production
- Kubernetes cluster (optional)
- Separate database server
- Redis cluster
- Nginx load balancer
- SSL certificates (Let's Encrypt)
- Monitoring and logging stack

## Monitoring & Observability

### Metrics
- Request latency
- Error rates
- Analysis queue depth
- Database performance
- Memory and CPU usage

### Logging
- Structured logging (JSON)
- Log aggregation
- Error tracking
- Audit trails

### Health Checks
- Service health endpoints
- Database connectivity
- External API availability
- Disk space monitoring

## Disaster Recovery

### Backup Strategy
- Daily database backups
- APK file backup
- Configuration version control
- Model snapshot storage

### High Availability
- Database replication
- Load balancer failover
- Session persistence
- Graceful degradation

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | Next.js | 14.0 |
| Backend | FastAPI | 0.104 |
| Database | PostgreSQL | 15 |
| Cache | Redis | 7 |
| Web Server | Nginx | Latest |
| Container | Docker | Latest |
| Orchestration | Docker Compose | 3.8 |
| Python | Python | 3.11 |
| Node.js | Node.js | 18 |

## API Communication Protocols

- **REST**: Standard HTTP/1.1 for CRUD operations
- **WebSocket**: Real-time updates (optional)
- **gRPC**: Internal service communication (optional)

## Future Enhancements

- Kubernetes deployment manifests
- GraphQL API option
- Mobile app (React Native)
- Advanced threat intelligence feeds
- Machine learning model improvements
- Distributed analysis across multiple nodes
