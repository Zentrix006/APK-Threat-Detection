# API Documentation

## Authentication

All API endpoints (except `/health` and `/docs`) require a JWT token in the `Authorization` header:

```
Authorization: Bearer {token}
```

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### APK Management

#### Upload APK
- **POST** `/apks/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: APK file

**Response**:
```json
{
  "id": "apk-123",
  "filename": "app.apk",
  "file_hash": "sha256hash",
  "status": "uploaded",
  "message": "APK uploaded successfully"
}
```

#### List APKs
- **GET** `/apks?skip=0&limit=20`

**Response**:
```json
{
  "total": 50,
  "skip": 0,
  "limit": 20,
  "apks": [
    {
      "id": "apk-123",
      "filename": "app.apk",
      "file_hash": "...",
      "status": "analyzed",
      "upload_date": "2024-01-15T10:30:00Z",
      "risk_level": "high"
    }
  ]
}
```

#### Get APK Details
- **GET** `/apks/{apk_id}`

**Response**:
```json
{
  "id": "apk-123",
  "filename": "app.apk",
  "file_hash": "...",
  "file_size": 5242880,
  "package_name": "com.example.app",
  "app_name": "Example App",
  "version_code": "100",
  "version_name": "1.0.0",
  "status": "analyzed",
  "upload_date": "2024-01-15T10:30:00Z",
  "analysis_count": 2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Delete APK
- **DELETE** `/apks/{apk_id}`

**Response**:
```json
{
  "message": "APK deleted successfully"
}
```

### Analysis

#### Run Static Analysis
- **POST** `/analysis/static/{apk_id}`

**Response**:
```json
{
  "analysis_id": "analysis-456",
  "status": "queued",
  "message": "Static analysis queued"
}
```

#### Run Dynamic Analysis
- **POST** `/analysis/dynamic/{apk_id}`

**Response**:
```json
{
  "analysis_id": "analysis-457",
  "status": "queued",
  "message": "Dynamic analysis queued (requires Android emulator)"
}
```

#### Get Analysis Results
- **GET** `/analysis/{analysis_id}`

**Response**:
```json
{
  "id": "analysis-456",
  "apk_id": "apk-123",
  "type": "static",
  "status": "completed",
  "risk_score": 75.5,
  "risk_level": "high",
  "findings": {
    "permissions": ["android.permission.CAMERA", "android.permission.RECORD_AUDIO"],
    "urls": ["http://example.com", "http://malicious.com"],
    "suspicious_apis": ["java.lang.Runtime.exec", "java.net.Socket"],
    "c2_communications": []
  },
  "started_at": "2024-01-15T10:31:00Z",
  "completed_at": "2024-01-15T10:35:00Z",
  "duration": 240
}
```

#### Get Risk Score
- **GET** `/analysis/{apk_id}/risk-score`

**Response**:
```json
{
  "apk_id": "apk-123",
  "risk_score": 75.5,
  "risk_level": "high",
  "classifications": [
    {
      "type": "trojan",
      "subtype": "command_control",
      "confidence": 0.8
    },
    {
      "type": "spyware",
      "subtype": "surveillance",
      "confidence": 0.7
    }
  ],
  "confidence": 0.75
}
```

### Reports

#### Generate Report
- **POST** `/reports/generate/{apk_id}`

**Response**:
```json
{
  "report_id": "report-789",
  "status": "queued",
  "message": "Report generation started"
}
```

#### Get Report
- **GET** `/reports/{report_id}`

**Response**:
```json
{
  "id": "report-789",
  "apk_id": "apk-123",
  "type": "executive_summary",
  "status": "completed",
  "title": "Threat Intelligence Report: app.apk",
  "summary": "The analyzed APK exhibits multiple indicators of malicious behavior...",
  "created_at": "2024-01-15T10:36:00Z",
  "updated_at": "2024-01-15T10:40:00Z",
  "pdf_available": true
}
```

#### Download Report
- **GET** `/reports/{report_id}/download`

Returns PDF file

#### List Reports for APK
- **GET** `/reports/apk/{apk_id}`

**Response**:
```json
{
  "apk_id": "apk-123",
  "total": 3,
  "reports": [
    {
      "id": "report-789",
      "type": "executive_summary",
      "status": "completed",
      "created_at": "2024-01-15T10:40:00Z",
      "ai_generated": true
    }
  ]
}
```

## Error Responses

All errors return JSON with status code and message:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200`: Success
- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not found (resource doesn't exist)
- `500`: Internal server error
- `503`: Service unavailable

## Rate Limiting

- **General endpoints**: 10 requests/second
- **API endpoints**: 30 requests/second
- **Burst allowance**: 2x the per-second limit

Rate limit headers:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp for reset

## Pagination

List endpoints support pagination:

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 20, max: 100)

## Webhooks (Optional)

Configure webhooks for analysis completion:

```bash
POST /api/v1/webhooks/register
{
  "url": "https://your-domain.com/webhook",
  "events": ["analysis.completed", "report.generated"]
}
```

## API Examples

### Complete Analysis Workflow

```bash
# 1. Upload APK
curl -X POST http://localhost:8000/api/v1/apks/upload \
  -F "file=@app.apk" \
  -H "Authorization: Bearer $TOKEN"

# Response: {"id": "apk-123", ...}

# 2. Run static analysis
curl -X POST http://localhost:8000/api/v1/analysis/static/apk-123 \
  -H "Authorization: Bearer $TOKEN"

# Response: {"analysis_id": "analysis-456", "status": "queued"}

# 3. Check analysis status (poll)
curl http://localhost:8000/api/v1/analysis/analysis-456 \
  -H "Authorization: Bearer $TOKEN"

# 4. Generate report
curl -X POST http://localhost:8000/api/v1/reports/generate/apk-123 \
  -H "Authorization: Bearer $TOKEN"

# 5. Download report
curl http://localhost:8000/api/v1/reports/report-789/download \
  -H "Authorization: Bearer $TOKEN" \
  -o threat_report.pdf
```

## SDK Examples

### Python
```python
import requests

api_url = "http://localhost:8000/api/v1"
headers = {"Authorization": f"Bearer {token}"}

# Upload APK
with open("app.apk", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{api_url}/apks/upload", files=files, headers=headers)
    apk_id = response.json()["id"]

# Run analysis
requests.post(f"{api_url}/analysis/static/{apk_id}", headers=headers)

# Get risk score
risk = requests.get(f"{api_url}/analysis/{apk_id}/risk-score", headers=headers)
print(f"Risk Score: {risk.json()['risk_score']}")
```

### JavaScript
```javascript
const apiUrl = "http://localhost:8000/api/v1";
const token = "your-jwt-token";

// Upload APK
const formData = new FormData();
formData.append('file', apkFile);

const uploadResponse = await fetch(`${apiUrl}/apks/upload`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
const { id: apkId } = await uploadResponse.json();

// Get risk score
const riskResponse = await fetch(`${apiUrl}/analysis/${apkId}/risk-score`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const riskData = await riskResponse.json();
console.log(`Risk Score: ${riskData.risk_score}`);
```
