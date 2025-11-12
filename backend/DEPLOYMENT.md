# FastAPI Backend Deployment Guide

## Quick Start

### 1. Start All Services

```bash
cd n8n
docker-compose up -d
```

This starts:
- **n8n** (port 5678) - Workflow automation
- **backend** (port 8000) - FastAPI API
- **image-viewer** (port 8080) - Python image gallery

### 2. Verify Services

```bash
# Check all containers
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check n8n health
curl http://localhost:5678/healthz

# Check image viewer
curl http://localhost:8080/api/images
```

### 3. Access Services

- **FastAPI Docs**: http://localhost:8000/docs
- **n8n Interface**: http://localhost:5678 (admin/changeme123)
- **Image Gallery**: http://localhost:8080
- **ESP32 Camera**: http://10.0.0.30

## Environment Configuration

Create/update `.env` file in project root:

```bash
# WiFi (2.4GHz only!)
WIFI_SSID=FOOTBALL
WIFI_PASSWORD=cities3976

# ESP32
ESP32_IP=10.0.0.30

# OpenAI (optional)
OPENAI_API_KEY=sk-your-key-here

# Sensors (optional)
MOTION_SENSOR_ENABLED=true
LCD_SCREEN_ENABLED=true
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f n8n

# Rebuild backend
docker-compose build backend
docker-compose up -d backend

# Restart single service
docker-compose restart backend
```

## Testing the API

```bash
# Test ESP32 connection
curl http://localhost:8000/api/v1/esp32/ping

# Capture image
curl -X POST "http://localhost:8000/api/v1/camera/capture?label=test"

# List images
curl http://localhost:8000/api/v1/camera/images

# Check n8n status
curl http://localhost:8000/api/v1/n8n/status

# Record motion event
curl -X POST http://localhost:8000/api/v1/sensors/motion/event \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "pir_1", "confidence": 0.9}'
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose build --no-cache backend
docker-compose up -d backend
```

### ESP32 not reachable
- Verify ESP32 is on 2.4GHz WiFi (not 5GHz)
- Check IP address: `ping 10.0.0.30`
- Verify WiFi credentials in `.env`

### n8n connection failed
```bash
# Check n8n is running
docker-compose ps n8n

# Check n8n logs
docker-compose logs n8n

# Restart n8n
docker-compose restart n8n
```

## Production Deployment

1. **Set environment to production**
```bash
ENVIRONMENT=production
```

2. **Enable HTTPS** (use nginx reverse proxy)

3. **Add authentication** (implement JWT or API keys)

4. **Configure CORS** properly for your domain

5. **Set up monitoring** (Prometheus, Grafana)

6. **Enable rate limiting**

7. **Use secrets management** (Docker secrets, Vault)

## Health Monitoring

All services have health checks every 10 seconds:

```bash
# Check health status
docker ps

# Manual health checks
curl http://localhost:8000/health
curl http://localhost:5678/healthz
curl http://localhost:8080/api/images
```

## Backup & Restore

```bash
# Backup n8n data
docker run --rm -v esp32-webserver_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n-backup.tar.gz /data

# Restore n8n data
docker run --rm -v esp32-webserver_n8n_data:/data -v $(pwd):/backup alpine tar xzf /backup/n8n-backup.tar.gz -C /

# Backup captures
tar czf captures-backup.tar.gz captures/
```

## Performance Tuning

### Backend
- Adjust worker count: `uvicorn app.main:app --workers 4`
- Enable caching for image metadata
- Use Redis for sensor data storage

### n8n
- Increase execution timeout
- Enable workflow caching
- Use database backend (PostgreSQL)

## Security Checklist

- [ ] Change default n8n password
- [ ] Set strong WiFi password
- [ ] Enable HTTPS
- [ ] Add API authentication
- [ ] Restrict CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Implement rate limiting

---

**Need help?** Check the full documentation:
- Backend API: http://localhost:8000/docs
- API Endpoints: `backend/API_ENDPOINTS.md`
- Backend README: `backend/README.md`
