# 🚀 CryptoAnalyzer Pro - Installation Guide (FIXED VERSION)

## 📋 **OVERVIEW**

This is the **FIXED VERSION** of CryptoAnalyzer Pro that resolves all the critical issues reported:
- ✅ Backend structure corrected
- ✅ ImportError in alert_system.py resolved
- ✅ Rate limiting implemented
- ✅ Frontend dependencies stabilized
- ✅ Docker Compose fully functional

## 🔧 **PREREQUISITES**

### System Requirements:
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Verify Prerequisites:
```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker ps
```

## 📦 **QUICK START (5 MINUTES)**

### 1. **Extract Project**
```bash
# Extract the ZIP file
unzip CryptoAnalyzer_FIXED_FINAL.zip
cd CryptoAnalyzer_FIXED_FINAL
```

### 2. **Environment Setup**
```bash
# Copy environment file
cp .env.example .env

# Edit environment variables (optional)
nano .env
```

### 3. **Build and Start**
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. **Verify Installation**
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check nginx proxy
curl http://localhost/api/health
```

### 5. **Access Application**
- **Frontend**: http://localhost
- **API Documentation**: http://localhost/api/docs
- **Backend Direct**: http://localhost:8000

## 🔐 **LOGIN CREDENTIALS**

```
Email: admin@cryptoanalyzer.com
Password: admin123
```

---

## 📖 **DETAILED INSTALLATION**

### **Step 1: Project Structure**
```
CryptoAnalyzer_FIXED_FINAL/
├── backend/                 # FastAPI backend
│   ├── main.py             # ✅ Fixed location
│   ├── api/                # ✅ Correct structure
│   ├── core/               # ✅ Configuration
│   ├── services/           # ✅ Fixed imports
│   ├── models/             # ✅ Database models
│   ├── requirements.txt    # ✅ Stable versions
│   └── Dockerfile          # ✅ Tested build
├── frontend/               # React frontend
│   ├── src/                # ✅ TypeScript components
│   ├── package.json        # ✅ Fixed dependencies
│   └── Dockerfile          # ✅ Multi-stage build
├── nginx/                  # Reverse proxy
│   ├── nginx.conf          # ✅ Main config
│   └── default.conf        # ✅ Server config
├── docker-compose.yml      # ✅ Fully functional
└── .env.example            # ✅ All variables
```

### **Step 2: Environment Configuration**

#### **Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://crypto_user:crypto_pass@postgres:5432/crypto_db
POSTGRES_DB=crypto_db
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_pass

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Security
SECRET_KEY=your-secret-key-change-in-production
```

#### **Optional API Keys:**
```bash
# CoinGecko (for real data)
COINGECKO_API_KEY=your-api-key

# Alerts
TELEGRAM_BOT_TOKEN=your-bot-token
DISCORD_WEBHOOK_URL=your-webhook-url
```

### **Step 3: Build Process**

#### **Build All Services:**
```bash
# Build with no cache (clean build)
docker-compose build --no-cache

# Build specific service
docker-compose build backend
docker-compose build frontend
```

#### **Expected Build Output:**
```
✅ postgres: Pulled
✅ redis: Pulled  
✅ backend: Built successfully
✅ frontend: Built successfully
✅ nginx: Pulled
```

### **Step 4: Service Startup**

#### **Start Services:**
```bash
# Start in background
docker-compose up -d

# Start with logs (for debugging)
docker-compose up

# Start specific services
docker-compose up -d postgres redis
docker-compose up -d backend
docker-compose up -d frontend nginx
```

#### **Check Service Health:**
```bash
# View all containers
docker-compose ps

# Expected output:
# NAME              STATUS
# crypto_postgres   Up (healthy)
# crypto_redis      Up (healthy)
# crypto_backend    Up (healthy)
# crypto_celery     Up
# crypto_frontend   Up
# crypto_nginx      Up
```

### **Step 5: Verification**

#### **Health Checks:**
```bash
# Backend API
curl -f http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}

# Frontend
curl -f http://localhost:3000
# Expected: HTML content

# Nginx Proxy
curl -f http://localhost/api/health
# Expected: {"status":"healthy"}
```

#### **Service Logs:**
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f backend
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **1. Backend Won't Start**
```bash
# Check logs
docker-compose logs backend

# Common fixes:
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

#### **2. Frontend Build Fails**
```bash
# Check Node.js version in container
docker-compose exec frontend node --version

# Rebuild with clean cache
docker-compose down
docker system prune -f
docker-compose build --no-cache frontend
docker-compose up -d
```

#### **3. Database Connection Issues**
```bash
# Check PostgreSQL
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait 30 seconds
docker-compose up -d backend
```

#### **4. Port Conflicts**
```bash
# Check what's using ports
netstat -tulpn | grep :80
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop nginx
```

#### **5. Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### **Debug Commands**

#### **Container Inspection:**
```bash
# Enter backend container
docker-compose exec backend bash

# Enter frontend container  
docker-compose exec frontend sh

# Check container resources
docker stats

# Inspect container
docker inspect crypto_backend
```

#### **Network Debugging:**
```bash
# Test internal connectivity
docker-compose exec backend ping postgres
docker-compose exec backend ping redis
docker-compose exec frontend ping backend

# Check network
docker network ls
docker network inspect cryptoanalyzer_crypto_network
```

### **Performance Optimization**

#### **Resource Limits:**
```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

#### **Monitoring:**
```bash
# Resource usage
docker-compose exec backend htop
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Disk usage
docker system df
docker-compose exec backend df -h
```

---

## 🚀 **ADVANCED CONFIGURATION**

### **Production Deployment**

#### **Environment Variables:**
```bash
# Production settings
DEBUG=false
SECRET_KEY=generate-strong-secret-key
ALLOWED_HOSTS=["yourdomain.com"]

# Database (use external)
DATABASE_URL=postgresql://user:pass@your-db-host:5432/crypto_db

# Redis (use external)
REDIS_URL=redis://your-redis-host:6379/0
```

#### **SSL/HTTPS Setup:**
```bash
# Add to nginx/default.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    # ... rest of config
}
```

### **Scaling Services**

#### **Multiple Workers:**
```yaml
# In docker-compose.yml
celery_worker:
  # ... existing config
  deploy:
    replicas: 3
```

#### **Load Balancing:**
```yaml
backend:
  # ... existing config
  deploy:
    replicas: 2
```

### **Backup & Recovery**

#### **Database Backup:**
```bash
# Create backup
docker-compose exec postgres pg_dump -U crypto_user crypto_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U crypto_user crypto_db < backup.sql
```

#### **Volume Backup:**
```bash
# Backup volumes
docker run --rm -v cryptoanalyzer_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v cryptoanalyzer_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

---

## ✅ **VERIFICATION CHECKLIST**

### **Installation Complete When:**
- [ ] All containers show "Up (healthy)" status
- [ ] Backend health check returns 200 OK
- [ ] Frontend loads at http://localhost
- [ ] API docs accessible at http://localhost/api/docs
- [ ] Login works with demo credentials
- [ ] Dashboard displays cryptocurrency data
- [ ] No error logs in any service

### **Success Indicators:**
```bash
# All these should return success:
curl -f http://localhost/health                    # ✅ 200 OK
curl -f http://localhost/api/health               # ✅ 200 OK  
curl -f http://localhost/api/crypto/list          # ✅ JSON data
docker-compose ps | grep -c "Up"                 # ✅ 6 services
```

---

## 📞 **SUPPORT**

### **If You Encounter Issues:**

1. **Check this guide first** - Most issues are covered
2. **Review logs** - `docker-compose logs [service]`
3. **Verify prerequisites** - Docker version, ports, permissions
4. **Try clean rebuild** - `docker-compose down && docker-compose build --no-cache`
5. **Contact support** - Provide logs and error messages

### **Log Collection:**
```bash
# Collect all logs for support
docker-compose logs > cryptoanalyzer-logs.txt
docker-compose ps > cryptoanalyzer-status.txt
docker system info > docker-info.txt
```

**🎉 CONGRATULATIONS! You now have a fully functional CryptoAnalyzer Pro system!**

