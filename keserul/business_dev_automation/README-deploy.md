# Business Development Automation - Deployment Guide

**🚀 One-Command Production Deployment**

This guide provides step-by-step instructions for deploying the Business Development Automation System to production.

## 📋 Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- Minimum 4GB RAM, 2 CPU cores
- 50GB available disk space
- Domain name with DNS access (for SSL certificates)

## ⚡ Quick Start (One Command)

```bash
curl -fsSL https://raw.githubusercontent.com/company/bizdev-automation/main/deploy.sh | bash
```

This script will:
1. Clone the repository
2. Set up environment variables interactively
3. Create required directories and config files
4. Deploy the full stack with monitoring
5. Verify deployment health

## 🔧 Manual Deployment

### Step 1: Clone Repository
```bash
git clone https://github.com/company/bizdev-automation.git
cd bizdev-automation/business_dev_automation
```

### Step 2: Environment Setup
```bash
# Copy example environment file
cp .env.example .env

# Edit with your values (required secrets below)
nano .env
```

**Required Environment Variables:**
```bash
# API Keys (REQUIRED)
SENDGRID_API_KEY=your_sendgrid_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Redis Cache (REQUIRED)
REDIS_PASSWORD=your_secure_redis_password

# Google Sheets Configuration (REQUIRED)
GOOGLE_SHEETS_SPREADSHEET_ID=your_google_sheets_spreadsheet_id

# Monitoring (REQUIRED)
GRAFANA_PASSWORD=your_grafana_admin_password

# Domain & SSL (REQUIRED for production)
DOMAIN_NAME=bizdev.yourcompany.com
CLOUDFLARE_EMAIL=your_cloudflare_email
CLOUDFLARE_API_KEY=your_cloudflare_api_key

# Email Configuration (REQUIRED)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
EMAIL_FROM=noreply@yourcompany.com
```

### Step 3: Create Required Directories and Credentials
```bash
mkdir -p {output,logs,config/{grafana/dashboards,grafana/datasources},credentials}

# Copy your Google Sheets service account credentials
cp /path/to/your/sheets-service-account.json credentials/
```

### Step 4: Deploy Services
```bash
# Deploy all services
docker compose -f docker-compose.prod.yml up -d

# Check deployment status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

## 🎯 Verification Steps

### 1. Health Checks
```bash
# Check all services are running
docker compose -f docker-compose.prod.yml ps

# Verify API health
curl -f http://localhost:8000/api/health

# Check Redis connectivity
docker exec bizdev_redis redis-cli ping

# Check Google Sheets connectivity
curl -X GET http://localhost:8000/api/sheets/health
```

### 2. Service Endpoints
- **API Gateway:** http://localhost:8000
- **Grafana Dashboard:** http://localhost:3000 (admin/your_grafana_password)
- **Prometheus Metrics:** http://localhost:9090
- **Traefik Dashboard:** http://localhost:8080

### 3. Test API Endpoints
```bash
# Test lead generation endpoint
curl -X POST http://localhost:8000/api/leadgen/run \
  -H "Content-Type: application/json" \
  -d '{"sources": ["SGTech"], "limit": 5}'

# Test health endpoint
curl http://localhost:8000/api/health

# Test metrics endpoint
curl http://localhost:8000/api/metrics
```

## 📊 Monitoring & Alerting

### Grafana Setup
1. Access Grafana at http://localhost:3000
2. Login with admin/your_grafana_password
3. Import pre-configured dashboards from `/config/grafana/dashboards/`
4. Configure alert notifications (Slack, email, etc.)

### Key Metrics to Monitor
- **Request Rate:** API requests per minute
- **Error Rate:** 4xx/5xx error percentage  
- **Latency:** 95th percentile response time
- **Resource Usage:** CPU, memory, disk usage
- **Worker Health:** Lead generation, outreach, research workers

### Alerts Configuration
- High error rate (>5% for 5 minutes)
- High latency (>2s 95th percentile for 5 minutes)
- Worker failures (any worker down for >2 minutes)
- Resource exhaustion (>80% CPU/memory for 10 minutes)

## 🔧 Scaling & Performance

### Horizontal Scaling
```bash
# Scale lead generation workers
docker compose -f docker-compose.prod.yml up -d --scale leadgen_worker=5

# Scale outreach workers  
docker compose -f docker-compose.prod.yml up -d --scale outreach_worker=3

# Verify scaling
docker compose -f docker-compose.prod.yml ps
```

### Performance Tuning
```bash
# Run load tests
cd business_dev_automation
python3 -m locust -f locustfile.py --host=http://localhost:8000 \
  --users=100 --spawn-rate=10 --run-time=5m --headless

# Check performance metrics
curl http://localhost:8000/api/metrics
```

### Expected Performance
- **50 concurrent users:** >10 req/sec, <2s 95th percentile
- **100 concurrent users:** >15 req/sec, <3s 95th percentile
- **250 concurrent users:** >20 req/sec, <5s 95th percentile

## 🔒 Security & Compliance

### SSL/TLS Setup
```bash
# Automatic SSL with Let's Encrypt (requires domain)
# Edit docker-compose.prod.yml with your domain
# Traefik will automatically obtain SSL certificates

# Manual SSL certificate setup
mkdir -p certs/
# Copy your SSL certificates to certs/ directory
```

### Security Scanning
```bash
# Run dependency vulnerability scan
pip-audit --format=json --output=security_scan.json

# Container vulnerability scan
docker scout cves bizdev_orchestrator:latest

# Check compliance status
python3 scripts/compliance_check.py
```

### Backup & Recovery
```bash
# Backup Google Sheets data
python3 scripts/backup_sheets_data.py --spreadsheet-id=your_id --output=./backups/

# Backup Redis data  
docker exec bizdev_redis redis-cli BGSAVE

# Export data to CSV
python3 scripts/export_sheets_to_csv.py --all-worksheets
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check logs for specific service
docker compose -f docker-compose.prod.yml logs orchestrator

# Check resource usage
docker stats

# Restart specific service
docker compose -f docker-compose.prod.yml restart orchestrator
```

#### 2. Data Storage Connection Issues
```bash
# Check Google Sheets API connectivity
curl -X GET http://localhost:8000/api/sheets/health

# Check Redis logs  
docker compose -f docker-compose.prod.yml logs redis

# Test Redis connectivity
docker exec bizdev_redis redis-cli ping
```

#### 3. API Errors
```bash
# Check orchestrator logs
docker compose -f docker-compose.prod.yml logs orchestrator

# Check worker logs
docker compose -f docker-compose.prod.yml logs leadgen_worker

# Test API directly
curl -v http://localhost:8000/api/health
```

### Log Locations
- **Application logs:** `./logs/` directory
- **Container logs:** `docker compose logs <service_name>`
- **System logs:** Grafana Loki at http://localhost:3100

## 🔄 Updates & Maintenance

### Rolling Updates
```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Perform rolling update
docker compose -f docker-compose.prod.yml up -d

# Verify deployment
docker compose -f docker-compose.prod.yml ps
```

### Maintenance Tasks
```bash
# Clean up old containers and images
docker system prune -a -f

# Rotate logs (if needed)
docker compose -f docker-compose.prod.yml exec orchestrator logrotate /etc/logrotate.conf

# Update SSL certificates (automatic with Let's Encrypt)
docker compose -f docker-compose.prod.yml restart traefik
```

## 📞 Support

### Health Endpoints
- **System Health:** `GET /api/health`
- **Detailed Status:** `GET /api/status`
- **Metrics:** `GET /api/metrics`

### Emergency Contacts
- **DevOps Team:** devops@company.com
- **Security Team:** security@company.com
- **On-call Engineer:** +1-555-ON-CALL

### Documentation Links
- **API Documentation:** http://localhost:8000/api/docs
- **Architecture Overview:** [README.md](README.md)
- **Security Guide:** [compliance/security_checklist.md](compliance/security_checklist.md)

---

## 📝 Quick Reference Commands

```bash
# Deploy
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Scale workers
docker compose -f docker-compose.prod.yml up -d --scale leadgen_worker=3

# Stop all services
docker compose -f docker-compose.prod.yml down

# Stop and remove all data
docker compose -f docker-compose.prod.yml down -v
```

**🎉 Your Business Development Automation System is now running!**

Access the API at http://localhost:8000 and Grafana dashboard at http://localhost:3000 