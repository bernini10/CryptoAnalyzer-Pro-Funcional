
# 🔧 CryptoAnalyzer Pro - Troubleshooting Guide

## 🚨 **CRITICAL ISSUES RESOLVED**

This version fixes all the major problems reported:

### **✅ FIXED: Backend Structure Issues**
- **Problem**: `ModuleNotFoundError` due to incorrect file structure
- **Solution**: Moved `main.py` to correct location, fixed all imports
- **Verification**: `docker-compose logs backend` shows no import errors

### **✅ FIXED: ImportError in alert_system.py**
- **Problem**: `ALERT_CONFIG` variable not found
- **Solution**: Defined `ALERT_CONFIG` locally in the module
- **Verification**: Celery worker starts without errors

### **✅ FIXED: API Rate Limiting**
- **Problem**: Too many requests to CoinGecko API causing 429 errors
- **Solution**: Implemented 2-second delays and retry logic
- **Verification**: No more throttling errors in logs

### **✅ FIXED: Frontend Dependencies**
- **Problem**: React Scripts 5.0.1 dependency conflicts
- **Solution**: Downgraded to React Scripts 4.0.3 with fixed TypeScript version
- **Verification**: `npm install` and `npm run build` work without errors

### **✅ FIXED: Docker Compose Issues**
- **Problem**: Services failing to start due to configuration errors
- **Solution**: Corrected all service configurations and health checks
- **Verification**: All services show "Up (healthy)" status

---

## 🔍 **DIAGNOSTIC COMMANDS**

### **Quick Health Check**
```bash
# Run this first to check overall system health
./health-check.sh

# Or manually:
echo "=== SYSTEM STATUS ==="
docker-compose ps
echo "=== BACKEND HEALTH ==="
curl -f http://localhost:8000/health
echo "=== FRONTEND HEALTH ==="
curl -f http://localhost:3000
echo "=== NGINX PROXY ==="
curl -f http://localhost/api/health
```

### **Service-Specific Diagnostics**

#### **Backend Diagnostics:**
```bash
# Check backend logs
docker-compose logs backend | tail -50

# Check if backend is responding
curl -v http://localhost:8000/health

# Test API endpoints
curl http://localhost:8000/api/crypto/list
curl http://localhost:8000/api/dashboard

# Check database connection
docker-compose exec backend python -c "
from core.database import engine
import asyncio
async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database OK:', result.scalar())
asyncio.run(test())
"
```

#### **Frontend Diagnostics:**
```bash
# Check frontend logs
docker-compose logs frontend | tail -50

# Check if frontend is building
docker-compose exec frontend npm run build

# Test frontend directly
curl -I http://localhost:3000

# Check for JavaScript errors
docker-compose exec frontend npm test -- --watchAll=false
```

#### **Database Diagnostics:**
```bash
# Check PostgreSQL logs
docker-compose logs postgres | tail -50

# Connect to database
docker-compose exec postgres psql -U crypto_user -d crypto_db

# Check database status
docker-compose exec postgres pg_isready -U crypto_user -d crypto_db

# View database size
docker-compose exec postgres psql -U crypto_user -d crypto_db -c "\l+"
```

#### **Redis Diagnostics:**
```bash
# Check Redis logs
docker-compose logs redis | tail -50

# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis info
docker-compose exec redis redis-cli info

# Monitor Redis commands
docker-compose exec redis redis-cli monitor
```

---

## 🐛 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: "ModuleNotFoundError" in Backend**

**Symptoms:**
```
ModuleNotFoundError: No module named 'api'
ModuleNotFoundError: No module named 'core'
ModuleNotFoundError: No module named 'services'
```

**Root Cause:** Incorrect file structure or PYTHONPATH

**Solution:**
```bash
# 1. Verify correct structure
ls -la backend/
# Should show: main.py, api/, core/, services/, models/

# 2. Rebuild backend
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d backend

# 3. Check logs
docker-compose logs backend
```

**Prevention:** Don't move `main.py` from backend root directory

---

### **Issue 2: "ImportError: cannot import name 'ALERT_CONFIG'"**

**Symptoms:**
```
ImportError: cannot import name 'ALERT_CONFIG' from 'services.alert_system'
```

**Root Cause:** Missing configuration variable

**Solution:**
```bash
# 1. Check if alert_system.py has ALERT_CONFIG defined
docker-compose exec backend grep -n "ALERT_CONFIG" services/alert_system.py

# 2. If missing, the file is corrupted. Rebuild:
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

# 3. Verify Celery worker starts
docker-compose logs celery_worker
```

**Prevention:** Don't modify services/alert_system.py

---

### **Issue 3: "429 Too Many Requests" from CoinGecko**

**Symptoms:**
```
HTTP 429: Throttled
Rate limit exceeded
```

**Root Cause:** Too many API requests without delays

**Solution:**
```bash
# 1. Check scheduler logs
docker-compose logs backend | grep -i "rate\|throttle\|429"

# 2. Verify rate limiting is working
docker-compose exec backend grep -n "rate_limit_delay" services/scheduler.py

# 3. Restart scheduler
docker-compose restart backend
```

**Prevention:** Don't modify the API call delays in scheduler.py

---

### **Issue 4: Frontend Build Fails with Dependency Conflicts**

**Symptoms:**
```
ERESOLVE unable to resolve dependency tree
Cannot find module 'ajv/dist/compile/codegen'
Unknown keyword formatMinimum
```

**Root Cause:** Incompatible dependency versions

**Solution:**
```bash
# 1. Check package.json versions
cat frontend/package.json | grep -E "(react-scripts|typescript)"

# 2. Clean rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache frontend

# 3. If still failing, check Node version
docker-compose run --rm frontend node --version
# Should be Node 16
```

**Prevention:** Don't upgrade react-scripts or TypeScript versions

---

### **Issue 5: "502 Bad Gateway" from Nginx**

**Symptoms:**
- Nginx returns 502 error
- Frontend/backend not accessible through proxy

**Root Cause:** Backend not responding or network issues

**Solution:**
```bash
# 1. Check if backend is running
docker-compose ps backend
curl http://localhost:8000/health

# 2. Check nginx logs
docker-compose logs nginx

# 3. Test internal connectivity
docker-compose exec nginx ping backend
docker-compose exec nginx ping frontend

# 4. Restart nginx
docker-compose restart nginx
```

**Prevention:** Ensure backend starts before nginx

---

### **Issue 6: Database Connection Refused**

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
Connection refused
```

**Root Cause:** PostgreSQL not ready or network issues

**Solution:**
```bash
# 1. Check PostgreSQL status
docker-compose ps postgres
docker-compose logs postgres

# 2. Wait for database to be ready
docker-compose exec postgres pg_isready -U crypto_user -d crypto_db

# 3. Restart in correct order
docker-compose down
docker-compose up -d postgres
# Wait 30 seconds
docker-compose up -d redis
docker-compose up -d backend
```

**Prevention:** Use health checks and depends_on in docker-compose.yml

---

### **Issue 7: High Memory Usage**

**Symptoms:**
- System becomes slow
- Containers getting killed (OOMKilled)

**Root Cause:** Insufficient memory allocation

**Solution:**
```bash
# 1. Check memory usage
docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 2. Add memory limits to docker-compose.yml
# (Already included in this version)

# 3. Increase system memory or reduce services
docker-compose down
docker-compose up -d postgres redis backend
# Start only essential services first
```

**Prevention:** Monitor memory usage regularly

---

## 🔧 **ADVANCED TROUBLESHOOTING**

### **Deep Debugging**

#### **Enable Debug Mode:**
```bash
# 1. Edit .env file
DEBUG=true

# 2. Restart services
docker-compose down
docker-compose up -d

# 3. Check verbose logs
docker-compose logs -f backend
```

#### **Container Shell Access:**
```bash
# Backend debugging
docker-compose exec backend bash
cd /app
python -c "import sys; print(sys.path)"
python -c "from core.config import settings; print(settings.DATABASE_URL)"

# Frontend debugging
docker-compose exec frontend sh
npm list
npm run build --verbose
```

#### **Network Debugging:**
```bash
# Check internal DNS resolution
docker-compose exec backend nslookup postgres
docker-compose exec backend nslookup redis

# Test port connectivity
docker-compose exec backend nc -zv postgres 5432
docker-compose exec backend nc -zv redis 6379

# Check network configuration
docker network inspect cryptoanalyzer_crypto_network
```

### **Performance Analysis**

#### **Database Performance:**
```bash
# Check slow queries
docker-compose exec postgres psql -U crypto_user -d crypto_db -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Check connections
docker-compose exec postgres psql -U crypto_user -d crypto_db -c "
SELECT count(*) as connections, state 
FROM pg_stat_activity 
GROUP BY state;"
```

#### **API Performance:**
```bash
# Test API response times
time curl http://localhost:8000/api/crypto/list
time curl http://localhost:8000/api/dashboard

# Check concurrent requests
ab -n 100 -c 10 http://localhost:8000/api/health
```

### **Log Analysis**

#### **Error Pattern Detection:**
```bash
# Find common errors
docker-compose logs backend 2>&1 | grep -i error | sort | uniq -c | sort -nr

# Check for memory issues
docker-compose logs 2>&1 | grep -i "memory\|oom\|killed"

# Monitor real-time errors
docker-compose logs -f 2>&1 | grep -i "error\|exception\|failed"
```

#### **Performance Monitoring:**
```bash
# Request timing
docker-compose logs nginx | grep -E "GET|POST" | awk '{print $NF}' | sort -n

# Database query timing
docker-compose logs backend | grep -i "query" | grep -oE "[0-9]+ms"
```

---

## 🚀 **OPTIMIZATION TIPS**

### **Performance Improvements**

#### **Database Optimization:**
```sql
-- Connect to database
docker-compose exec postgres psql -U crypto_user -d crypto_db

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON cryptocurrencies(symbol);
CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol);
```

#### **Redis Optimization:**
```bash
# Configure Redis for better performance
docker-compose exec redis redis-cli CONFIG SET maxmemory 256mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### **Frontend Optimization:**
```bash
# Enable production build optimizations
# Already configured in package.json and Dockerfile

# Check bundle size
docker-compose exec frontend npm run build
docker-compose exec frontend ls -lah build/static/js/
```

### **Resource Management**

#### **Memory Optimization:**
```yaml
# Add to docker-compose.yml (already included)
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

#### **CPU Optimization:**
```yaml
# Limit CPU usage (already included)
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
```

---

## 📊 **MONITORING & ALERTS**

### **Health Monitoring Script**

Create `monitor.sh`:
```bash
#!/bin/bash
# CryptoAnalyzer Health Monitor

echo "=== $(date) ==="
echo "Container Status:"
docker-compose ps

echo -e "\nHealth Checks:"
curl -s http://localhost:8000/health | jq .
curl -s http://localhost/api/health | jq .

echo -e "\nResource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo -e "\nDisk Usage:"
df -h | grep -E "(/$|/var/lib/docker)"

echo "========================"
```

### **Automated Monitoring**

#### **Cron Job Setup:**
```bash
# Add to crontab
*/5 * * * * /path/to/CryptoAnalyzer_FIXED_FINAL/monitor.sh >> /var/log/crypto-monitor.log 2>&1
```

#### **Alert Thresholds:**
```bash
# CPU > 80%
# Memory > 80%
# Disk > 90%
# Response time > 5s
```

---

## 📞 **GETTING HELP**

### **Before Contacting Support:**

1. **Run diagnostics:**
   ```bash
   docker-compose ps
   docker-compose logs --tail=100
   curl -v http://localhost:8000/health
   ```

2. **Collect system info:**
   ```bash
   docker version
   docker-compose version
   free -h
   df -h
   ```

3. **Check this guide** - Most issues are documented here

### **Support Information to Provide:**

- Operating system and version
- Docker and Docker Compose versions
- Complete error messages
- Service logs (`docker-compose logs`)
- System resources (`docker stats`)
- Steps to reproduce the issue

### **Emergency Recovery:**

If system is completely broken:
```bash
# Nuclear option - complete reset
docker-compose down -v
docker system prune -a -f
docker volume prune -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

**⚠️ Warning:** This will delete all data!

---

## ✅ **SUCCESS VERIFICATION**

### **System is Working When:**

- [ ] All containers show "Up (healthy)"
- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] API endpoints return data
- [ ] Login works with demo credentials
- [ ] Dashboard displays crypto data
- [ ] No critical errors in logs
- [ ] Memory usage < 80%
- [ ] CPU usage < 80%
- [ ] Response times < 2s

### **Final Test Script:**
```bash
#!/bin/bash
echo "Running final verification..."

# Test all endpoints
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000 || exit 1
curl -f http://localhost/api/health || exit 1
curl -f http://localhost/api/crypto/list || exit 1

echo "✅ All tests passed! System is fully operational."
```

**🎉 Your CryptoAnalyzer Pro system is now fully functional and optimized!**

