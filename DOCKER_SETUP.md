# 🐳 Docker Setup for ESP32 Camera + n8n

Complete Docker setup for running n8n automation with your ESP32 camera system.

## 🚀 Quick Start

### 1. Start Docker Services

```bash
docker-compose up -d
```

This starts:
- **n8n** on port 5678
- **Image Viewer API** on port 8080

### 2. Access Services

- **n8n Interface:** <http://localhost:5678>
  - Username: `admin`
  - Password: `changeme123` (⚠️ Change this!)
- **Image Gallery:** <http://localhost:8080>
- **ESP32 Camera:** <http://10.0.0.30>

### 3. Configure n8n

1. Open <http://localhost:5678>
2. Login with credentials above
3. Create your first workflow!

## 📦 What's Included

### Services

#### n8n (Workflow Automation)
- Latest n8n image
- Persistent data storage
- Basic authentication enabled
- Webhook support
- Access to ESP32 camera via host network

#### Image Viewer API
- Python-based REST API
- Image gallery web interface
- Persistent image storage
- Direct ESP32 camera integration

### Volumes

- `n8n_data`: Persistent n8n workflows and settings
- `./captures`: Shared image storage
- `./n8n-workflows`: Pre-configured workflows (optional)

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
# n8n Configuration
N8N_BASIC_AUTH_USER: admin          # Change username
N8N_BASIC_AUTH_PASSWORD: changeme123 # Change password!
GENERIC_TIMEZONE: America/New_York   # Your timezone

# Image Viewer Configuration
ESP32_IP: 10.0.0.30                 # Your ESP32 IP address
PORT: 8080                          # API server port
```

### Change Default Password

**IMPORTANT:** Change the default n8n password!

```yaml
environment:
  - N8N_BASIC_AUTH_PASSWORD=your_secure_password_here
```

## 🎯 Using n8n with ESP32

### API Endpoints (from n8n)

All endpoints accessible at `http://image-viewer:8080` from within Docker network, or `http://localhost:8080` from host.

#### Capture Image
```
GET http://image-viewer:8080/api/capture
```

#### List Images
```
GET http://image-viewer:8080/api/images
```

#### Rename Image
```
POST http://image-viewer:8080/api/rename
Body: {"old_name": "...", "new_label": "..."}
```

#### Delete Image
```
DELETE http://image-viewer:8080/api/delete/{filename}
```

### Example n8n Workflow

1. **Create New Workflow** in n8n
2. **Add Schedule Trigger**
   - Cron: `*/5 * * * *` (every 5 minutes)
3. **Add HTTP Request Node**
   - Method: GET
   - URL: `http://image-viewer:8080/api/capture`
4. **Add Set Node** (optional)
   - Extract filename from response
5. **Save & Activate**

## 🛠️ Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Just n8n
docker-compose logs -f n8n

# Just image viewer
docker-compose logs -f image-viewer
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

## 📁 Directory Structure

```
ESP32-webserver/
├── docker-compose.yml          # Main Docker configuration
├── Dockerfile.viewer           # Image viewer container
├── view_captures.py           # API server code
├── captures/                  # Persistent image storage
│   └── .gitkeep
└── n8n-workflows/            # Optional: Pre-made workflows
    └── esp32-camera.json
```

## 🔒 Security Notes

### Production Deployment

1. **Change Default Password**
   ```yaml
   N8N_BASIC_AUTH_PASSWORD: use_strong_password_here
   ```

2. **Use HTTPS**
   - Add reverse proxy (nginx/traefik)
   - Get SSL certificate (Let's Encrypt)

3. **Restrict Network Access**
   ```yaml
   ports:
     - "127.0.0.1:5678:5678"  # Only localhost
   ```

4. **Use Secrets**
   ```yaml
   environment:
     - N8N_BASIC_AUTH_PASSWORD_FILE=/run/secrets/n8n_password
   secrets:
     n8n_password:
       file: ./secrets/n8n_password.txt
   ```

## 🐛 Troubleshooting

### n8n Can't Access ESP32

**Problem:** n8n workflows can't reach ESP32 camera

**Solution:**
```yaml
# In docker-compose.yml, add to n8n service:
extra_hosts:
  - "host.docker.internal:host-gateway"

# Then use in n8n:
http://host.docker.internal:10.0.0.30/capture
```

Or use the image-viewer service as proxy:
```
http://image-viewer:8080/api/capture
```

### Images Not Persisting

**Problem:** Images disappear after container restart

**Solution:** Ensure volume is mounted:
```yaml
volumes:
  - ./captures:/app/captures
```

### Permission Issues

**Problem:** Can't write to captures folder

**Solution:**
```bash
chmod 777 captures/
```

Or run container as your user:
```yaml
user: "${UID}:${GID}"
```

### Port Already in Use

**Problem:** Port 5678 or 8080 already in use

**Solution:** Change ports in docker-compose.yml:
```yaml
ports:
  - "5679:5678"  # Use different host port
```

## 📊 Resource Usage

Typical resource consumption:

- **n8n**: 
  - RAM: ~200-300MB
  - CPU: <5% (idle), 10-20% (active)
- **Image Viewer**:
  - RAM: ~50-100MB
  - CPU: <1% (idle), 5-10% (serving)
- **Disk**: 
  - n8n data: ~100MB
  - Images: ~100KB per image

## 🔄 Backup & Restore

### Backup n8n Data
```bash
docker run --rm -v esp32-webserver_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n-backup.tar.gz /data
```

### Restore n8n Data
```bash
docker run --rm -v esp32-webserver_n8n_data:/data -v $(pwd):/backup alpine tar xzf /backup/n8n-backup.tar.gz -C /
```

### Backup Images
```bash
tar czf captures-backup.tar.gz captures/
```

## 🚀 Advanced Usage

### Add More Services

Edit `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Custom Network Configuration

```yaml
networks:
  esp32-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Health Checks

```yaml
services:
  n8n:
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📚 Next Steps

1. **Import Example Workflows**
   - See `n8n-workflows/` folder
   - Import via n8n UI

2. **Connect to AI Services**
   - OpenAI Vision
   - Google Cloud Vision
   - AWS Rekognition

3. **Set Up Notifications**
   - Email
   - Slack
   - Discord
   - Telegram

4. **Create Automations**
   - Motion detection alerts
   - Scheduled captures
   - AI-powered labeling
   - Cloud backup

## 🆘 Support

- **n8n Documentation:** <https://docs.n8n.io>
- **Docker Documentation:** <https://docs.docker.com>
- **Project Issues:** <https://github.com/gmossy/ESP32-WROVER-DEV/issues>

---

**Happy Automating!** 🤖📷

*Built with ❤️ by Glenn Mossy*
