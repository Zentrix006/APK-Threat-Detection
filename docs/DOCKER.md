# Docker deployment — APK Threat Intelligence Platform

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
```

| URL | Service |
|-----|---------|
| http://localhost | Nginx (recommended — proxies UI + API) |
| http://localhost:3000 | Next.js frontend |
| http://localhost:8000 | FastAPI backend + `/docs` |
| http://localhost:11434 | Ollama (AI reasoning & reports) |

## Investigation workflow

1. Open **http://localhost** (or port 3000).
2. **Upload APK** — triggers autonomous pipeline:
   - Static analysis (permissions, URLs, IPs, certs, obfuscation)
   - Optional dynamic analysis (`ENABLE_DYNAMIC_ANALYSIS=true` + ADB device)
   - AI threat reasoning (Ollama)
   - Threat graph, Malware Story, Digital Twin, Fraud Impact
3. Open investigation tabs: MITRE, graph, story, SOC report.

## Environment variables (Docker)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DB_NAME` | `apk_threat` | PostgreSQL database name |
| `OLLAMA_MODEL` | `qwen2.5:3b` | LLM for reasoning/reports |
| `ENABLE_DYNAMIC_ANALYSIS` | `false` | Set `true` when ADB sandbox is attached |
| `EMULATOR_HOST` | — | e.g. `host.docker.internal:5555` for host ADB |
| `VIRUSTOTAL_API_KEY` | — | Optional TI enrichment |

Pull an Ollama model after first start:

```bash
docker exec -it apk-threat-ollama ollama pull qwen2.5:3b
```

## Architecture

```
Browser → nginx:80 → frontend:3000
                  └→ backend:8000 (/api/v1/*)
backend → postgres, redis, ollama
```

Frontend uses **same-origin** `/api/v1/*` rewrites to `backend:8000` inside the Docker network.
