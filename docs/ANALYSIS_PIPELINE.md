# Analysis Pipeline Details

## Overview

The APK Threat Intelligence Platform employs a multi-stage analysis pipeline combining static analysis, dynamic analysis, machine learning, and AI to provide comprehensive threat assessment.

## Stage 1: Upload & Validation

### Steps
1. **File Receipt**
   - APK file uploaded via REST API
   - File size validation (max 500MB)
   - MIME type verification

2. **Storage**
   - File stored in persistent volume
   - SHA-256 hash calculated for deduplication
   - Metadata stored in PostgreSQL
   - File marked as "uploaded"

3. **Duplicate Detection**
   - Hash compared against existing APKs
   - If duplicate found, reuse previous analysis
   - Prevents redundant analysis

## Stage 2: Static Analysis

### Manifest Analysis
```
AndroidManifest.xml
├─ Package Information
│  ├─ Package name
│  ├─ Version code/name
│  └─ Min/target SDK
├─ Permissions
│  ├─ Declared permissions
│  ├─ Risk classification
│  └─ Usage context
├─ Components
│  ├─ Activities
│  ├─ Services
│  ├─ Broadcast Receivers
│  └─ Content Providers
└─ Intent Filters
   ├─ Implicit intents
   ├─ Custom schemes
   └─ Deep links
```

### Decompilation & Code Analysis
- **APKTool**: Extracts resources, manifest, assets
- **JADX**: Decompiles DEX to Java source
- **String Extraction**: 
  - URLs and domains
  - IP addresses
  - API endpoints
  - Hardcoded credentials
  - C2 domains

### Suspicious Indicator Detection
```
Categories:
├─ Cryptographic APIs
│  ├─ Cipher usage
│  ├─ Hash algorithms
│  └─ Key generation
├─ Networking
│  ├─ Socket creation
│  ├─ HTTP clients
│  └─ DNS queries
├─ Process Execution
│  ├─ Runtime.exec()
│  └─ ProcessBuilder
├─ Reflection
│  ├─ Class.forName()
│  └─ Method invocation
└─ File Operations
   ├─ File I/O
   └─ Database access
```

### Output
- Complete manifest XML
- Extracted strings
- Suspicious API list
- Permission analysis
- Component inventory

## Stage 3: Dynamic Analysis

### Environment Setup
1. **Emulator Preparation**
   - Android emulator initialization
   - Frida server deployment
   - Network monitoring setup
   - System state baseline

2. **APK Installation**
   - ADB push to device
   - APK installation
   - Permissions granting
   - File system setup

### Execution & Monitoring

#### Network Monitoring
```
Tools: tcpdump, scapy
Captures:
├─ TCP connections
├─ UDP communications
├─ DNS queries
├─ TLS/SSL handshakes
└─ Payload inspection
```

#### Runtime Instrumentation
```
Tool: Frida
Monitors:
├─ API calls (Java layer)
├─ System calls (native layer)
├─ File operations
├─ Permission usage
└─ Network activities
```

#### File System Monitoring
```
Observes:
├─ File creation/modification
├─ Database operations
├─ Cache usage
├─ Log file generation
└─ Temp file creation
```

#### Activity Capture
```
Records:
├─ Launched activities
├─ Services started
├─ Broadcasts sent
├─ Intents triggered
└─ Permission requests
```

### Output
- Network traffic dump (PCAP)
- API call logs
- File operations log
- Activity sequence
- System behavior profile

## Stage 4: Threat Detection & Scoring

### Indicator Extraction
```
From Static Analysis:
├─ Dangerous permissions
├─ Suspicious APIs
├─ Obfuscation patterns
├─ Hardcoded secrets
└─ Network indicators

From Dynamic Analysis:
├─ Outbound connections
├─ DNS queries
├─ File operations
├─ Sensitive API calls
└─ Behavior patterns
```

### Risk Scoring Algorithm

#### Feature Engineering
```python
features = [
    len(permissions),              # 0-1
    len(activities),               # 0-1
    len(services),                 # 0-1
    len(broadcast_receivers),      # 0-1
    len(content_providers),        # 0-1
    len(urls),                     # 0-1
    len(ips),                      # 0-1
    len(domains),                  # 0-1
    len(network_traffic),          # 0-1
    len(c2_communications),        # 0-1
    len(suspicious_apis),          # 0-1
    len(hardcoded_secrets),        # 0-1
    has_native_code,               # binary
    is_obfuscated,                 # binary
]
```

#### XGBoost Prediction
```
Input: Feature vector
Process:
├─ Feature normalization
├─ Tree ensemble evaluation
├─ Probability calculation
└─ Confidence scoring

Output:
├─ Malware probability (0-1)
├─ Risk score (0-100)
└─ Risk level (critical/high/medium/low)
```

#### Fallback Heuristic
If model unavailable:
```
score = 0.25 * permission_risk +
        0.20 * network_risk +
        0.20 * api_risk +
        0.15 * c2_risk +
        0.10 * encryption_risk +
        0.10 * obfuscation_risk
```

### C2 Detection
```
Indicators:
├─ Known C2 domains (regex patterns)
├─ Suspicious ports (4444, 5555, etc.)
├─ Command keywords
├─ Protocol anomalies
└─ Beaconing patterns
```

### Malware Classification
```
Classification Types:
├─ Trojan
│  ├─ Banking trojan
│  ├─ Spy trojan
│  └─ Command & Control
├─ Adware
│  ├─ Aggressive ads
│  └─ Generic adware
├─ PUA (Potentially Unwanted)
├─ Ransomware
├─ Spyware
│  ├─ Surveillance
│  └─ Data collection
├─ Rootkit
└─ Worm
```

## Stage 5: MITRE ATT&CK Mapping

### Framework Integration
```
ATT&CK Tactics:
├─ Reconnaissance
├─ Resource Development
├─ Initial Access
├─ Execution
├─ Persistence
├─ Privilege Escalation
├─ Defense Evasion
├─ Credential Access
├─ Discovery
├─ Collection
├─ Command & Control
├─ Exfiltration
└─ Impact
```

### Technique Mapping
```
Permission/API ──> Tactic ──> Technique
Examples:
├─ RECORD_AUDIO → Collection → T1429
├─ CAMERA → Collection → T1512
├─ ACCESS_FINE_LOCATION → Collection → T1430
├─ READ_SMS → Collection → T1407
├─ SEND_SMS → Impact → T1432
├─ INTERNET → C2 → T1571
└─ READ_CONTACTS → Collection → T1433
```

## Stage 6: AI Report Generation

### Context Preparation
```
Input Data:
├─ Risk score & level
├─ Permissions list
├─ Suspicious APIs
├─ Network indicators
├─ C2 communications
├─ MITRE mappings
├─ Dynamic behaviors
└─ Classification results
```

### LLM Processing
```
Tool: Ollama + Qwen3

Prompt Template:
├─ Analysis summary
├─ Key findings
├─ Threat indicators
├─ Behavioral patterns
└─ Context for analysis

Output:
├─ Executive summary
├─ Detailed findings
├─ Threat assessment
├─ Recommendations
└─ Confidence level
```

### Report Components
```
Generated Report:
├─ Header (title, date, analyst)
├─ Executive Summary
├─ Risk Assessment
│  ├─ Score
│  ├─ Level
│  └─ Classifications
├─ Technical Analysis
│  ├─ Permissions
│  ├─ APIs
│  ├─ Network
│  └─ Behaviors
├─ MITRE ATT&CK Mapping
├─ Indicators of Compromise (IoCs)
├─ Recommendations
└─ Appendices
```

## Stage 7: Report Export

### PDF Generation
- **Tool**: ReportLab
- **Features**:
  - Formatted tables
  - Charts and graphs
  - Risk score visualization
  - Professional styling
  - Watermarking (optional)

### Export Formats
```
├─ PDF (primary)
├─ JSON (structured data)
├─ HTML (interactive)
├─ CSV (indicators only)
└─ STIX 2.0 (threat intelligence)
```

## Pipeline Execution Flow

```
Upload
  ↓
Validation
  ↓
Store File
  ↓
Static Analysis
  ├─ Manifest parsing
  ├─ Decompilation
  ├─ String extraction
  └─ API detection
  ↓
Risk Calculation
  ├─ Feature extraction
  ├─ ML scoring
  └─ Classification
  ↓
Dynamic Analysis (Optional)
  ├─ Emulator execution
  ├─ Network capture
  ├─ API instrumentation
  └─ Behavior logging
  ↓
Threat Detection
  ├─ Indicator extraction
  ├─ C2 detection
  └─ Malware typing
  ↓
MITRE Mapping
  ├─ Tactic assignment
  └─ Technique mapping
  ↓
AI Report Generation
  ├─ LLM analysis
  ├─ Report formatting
  └─ PDF export
  ↓
Store Results
  ├─ Database
  ├─ Reports
  └─ Artifacts
  ↓
Complete
```

## Performance Metrics

### Timing
- **Static Analysis**: 30-120 seconds
- **Dynamic Analysis**: 300-600 seconds
- **Risk Scoring**: 1-5 seconds
- **Report Generation**: 10-30 seconds
- **Total (Static only)**: 1-3 minutes
- **Total (Hybrid)**: 5-15 minutes

### Accuracy
- **Detection Rate**: 85-92% (varies by malware type)
- **False Positive Rate**: 5-8%
- **Model Confidence**: 0.70-0.95

## Quality Assurance

### Validation Checks
- Manifest parsing verification
- Feature extraction validation
- Model prediction sanity checks
- Report completeness verification

### Error Handling
- Graceful fallbacks for missing tools
- Retry mechanisms for failures
- Timeout handling
- Error logging and alerting

## Future Improvements

- Ensemble models combining multiple ML approaches
- Behavioral clustering for unknown malware
- Graph analysis for complex APK relationships
- Incremental learning from analyst feedback
- Integration with threat feeds
- Real-time C2 domain updates
