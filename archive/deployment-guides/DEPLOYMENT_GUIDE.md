# OfferEarner VPS Deployment Guide

This guide documents the complete process of deploying the OfferEarner FastAPI application on a VPS with HestiaCP control panel.

## Prerequisites

- VPS with Ubuntu/Debian
- HestiaCP control panel installed
- SSH access to the server
- Domain or subdomain configured in HestiaCP

## Step 1: Initial Setup

### 1.1 Connect to your VPS
```bash
ssh ubuntu@your-server-ip
```

### 1.2 Navigate to your project directory
```bash
cd /home/raour/web/offerearner.raour.site/public_html
```

### 1.3 Set up virtual environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 2: Install Dependencies

### 2.1 Install all required packages
```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### 2.2 If you encounter missing dependencies, install them manually:
```bash
# Common missing dependencies we encountered:
pip install PyJWT
pip install pydantic[email]
pip install paypalrestsdk
pip install cryptography
```

### 2.3 Verify installation
```bash
# Test if the application starts
python start.py
```

## Step 3: Fix File Permissions

### 3.1 Set correct ownership
```bash
# Change ownership to the correct user (raour for HestiaCP)
sudo chown -R raour:raour /home/raour/web/offerearner.raour.site/public_html/

# Set proper permissions
sudo chmod -R 755 /home/raour/web/offerearner.raour.site/public_html/
sudo chmod 644 *.py
sudo chmod 644 *.db
sudo chmod -R 755 templates/
sudo chmod -R 755 static/
```

## Step 4: Configure Nginx Proxy

### 4.1 Using HestiaCP Web Interface
1. Log into HestiaCP: `https://your-server-ip:8083`
2. Go to **Web** → **offerearner.raour.site** → **Edit**
3. Enable **Proxy Support** or **Proxy Template**
4. Set **Proxy Target** to: `http://127.0.0.1:8001`
5. Click **Save**

### 4.2 Alternative: Custom Nginx Configuration
If proxy template doesn't work, add custom Nginx configuration:

```nginx
location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
}

location /static/ {
    proxy_pass http://127.0.0.1:8001/static/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Step 5: Handle Port Conflicts

### 5.1 If port 8000 is in use (e.g., by Docker)
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill processes using port 8000
sudo fuser -k 8000/tcp

# Or use a different port (recommended)
# Edit start.py to use port 8001
```

### 5.2 Update start.py for different port
```python
# In start.py, change the default port
port = int(os.getenv("PORT", "8001"))  # Changed from 8000 to 8001
```

## Step 6: Test the Application

### 6.1 Start the application
```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python start.py
```

### 6.2 Test locally
```bash
# Test if the application responds
curl http://127.0.0.1:8001
```

### 6.3 Test through domain
```bash
# Test the full domain
curl http://offerearner.raour.site
```

## Step 7: Set up Production Service

### 7.1 Create systemd service
```bash
sudo nano /etc/systemd/system/offerearner.service
```

Add this content:
```ini
[Unit]
Description=OfferEarner FastAPI Application
After=network.target

[Service]
User=raour
Group=raour
WorkingDirectory=/home/raour/web/offerearner.raour.site/public_html
Environment=PATH=/home/raour/web/offerearner.raour.site/public_html/venv/bin
ExecStart=/home/raour/web/offerearner.raour.site/public_html/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7.2 Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable offerearner
sudo systemctl start offerearner
sudo systemctl status offerearner
```

## Step 8: Environment Configuration

### 8.1 Create .env file
```bash
cd /home/raour/web/offerearner.raour.site/public_html
nano .env
```

Add production environment variables:
```
DATABASE_URL=sqlite:///./offerwall.db
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Step 9: Monitoring and Maintenance

### 9.1 Check service status
```bash
sudo systemctl status offerearner
```

### 9.2 View logs
```bash
# View service logs
sudo journalctl -u offerearner -f

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 9.3 Restart service
```bash
sudo systemctl restart offerearner
```

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError: No module named 'jwt'
**Solution:**
```bash
pip install PyJWT
```

### Issue 2: ModuleNotFoundError: No module named 'paypalrestsdk'
**Solution:**
```bash
pip install paypalrestsdk
```

### Issue 3: ImportError: email-validator is not installed
**Solution:**
```bash
pip install pydantic[email]
```

### Issue 4: Permission denied errors
**Solution:**
```bash
sudo chown -R raour:raour /home/raour/web/offerearner.raour.site/public_html/
sudo chmod -R 755 /home/raour/web/offerearner.raour.site/public_html/
```

### Issue 5: Port already in use
**Solution:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000

# Kill the process or use a different port
sudo fuser -k 8000/tcp
```

### Issue 6: 403 Access Denied error
**Causes:**
- Missing dependencies
- Incorrect file permissions
- Wrong user ownership
- Nginx proxy not configured

**Solution:**
1. Install all dependencies
2. Set correct file permissions
3. Configure Nginx proxy
4. Ensure application is running

## File Structure

```
/home/raour/web/offerearner.raour.site/public_html/
├── main.py                 # FastAPI application
├── start.py               # Startup script
├── requirements.txt        # Python dependencies
├── run.sh                 # Run script
├── venv/                  # Virtual environment
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS)
├── offerwall.db           # SQLite database
└── .env                   # Environment variables
```

## Security Considerations

1. **Change default secret key** in production
2. **Enable SSL/HTTPS** through HestiaCP
3. **Set up firewall** rules
4. **Regular backups** of database and files
5. **Monitor logs** for security issues

## Backup and Recovery

### Backup database
```bash
cp /home/raour/web/offerearner.raour.site/public_html/offerwall.db /backup/offerwall_$(date +%Y%m%d).db
```

### Backup entire application
```bash
tar -czf /backup/offerearner_$(date +%Y%m%d).tar.gz /home/raour/web/offerearner.raour.site/public_html/
```

## Troubleshooting Commands

```bash
# Check if service is running
sudo systemctl status offerearner

# Check if port is in use
sudo netstat -tlnp | grep :8001

# Check file permissions
ls -la /home/raour/web/offerearner.raour.site/public_html/

# Check Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# View real-time logs
sudo journalctl -u offerearner -f
```

## Quick Start Commands

For future deployments, use these commands:

```bash
# 1. Navigate to project
cd /home/raour/web/offerearner.raour.site/public_html

# 2. Activate venv and start
source venv/bin/activate
python start.py

# 3. Or use the run script
./run.sh

# 4. Or start the service
sudo systemctl start offerearner
```

---

**Last Updated:** 08/08/25
**Version:** 1.0
**Tested on:** Ubuntu with HestiaCP
