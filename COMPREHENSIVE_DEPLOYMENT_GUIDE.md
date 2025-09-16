# OfferEarner Comprehensive Deployment Guide

This guide covers deployment options for both the Node.js/TypeScript and Python/FastAPI versions of the OfferEarner application. Choose the technology stack that best fits your needs.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Technology Stack Options](#technology-stack-options)
- [Option 1: Node.js/TypeScript Deployment](#option-1-nodejstypescript-deployment)
- [Option 2: Python/FastAPI Deployment](#option-2-pythonfastapi-deployment)
- [Option 3: Docker Deployment](#option-3-docker-deployment)
- [Common Configuration](#common-configuration)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Prerequisites

- VPS with Ubuntu/Debian (recommended)
- SSH access to your server
- Domain or subdomain configured
- HestiaCP control panel (optional but recommended for traditional deployment)
- Docker and Docker Compose (for Docker deployment)
- Git access to your repository

## Technology Stack Options

### Node.js/TypeScript Version (Recommended)
- **Location**: Root directory (`/`)
- **Technology**: Node.js 18+, TypeScript, Express.js, Sequelize ORM
- **Database**: SQLite with Sequelize
- **Authentication**: JWT with bcrypt
- **Features**: PayPal integration, Lootably offerwall, modern TypeScript architecture

### Python/FastAPI Version (Reference Implementation)
- **Location**: `python-version/` directory
- **Technology**: Python 3.8+, FastAPI, SQLAlchemy ORM
- **Database**: SQLite with SQLAlchemy
- **Authentication**: JWT with bcrypt
- **Features**: Same functionality as Node.js version, Python implementation

## Option 1: Node.js/TypeScript Deployment

### Step 1: Server Setup

```bash
# Connect to your VPS
ssh ubuntu@your-server-ip

# Navigate to your web directory
cd /home/raour/web/your-domain.com/public_html
```

### Step 2: Install Node.js

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### Step 3: Deploy Application

```bash
# Clone or pull your repository
git clone https://github.com/your-username/OfferEarner-kilocode.git .
# OR if updating:
git pull origin main

# Install dependencies
npm install

# Build the application
npm run build
```

### Step 4: Environment Configuration

```bash
# Create .env file
nano .env
```

Add the following configuration:
```env
# Database
DATABASE_URL=sqlite:./offerwall.db

# Security
SECRET_KEY=your-super-secret-production-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
PORT=8001
NODE_ENV=production

# PayPal (optional)
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=sandbox

# Lootably (optional)
LOOTABLY_API_KEY=your-lootably-api-key
LOOTABLY_SECRET_KEY=your-lootably-secret-key
```

### Step 5: Set Permissions

```bash
# Set proper ownership (replace 'raour' with your username)
sudo chown -R raour:raour /home/raour/web/your-domain.com/public_html
sudo chmod -R 755 /home/raour/web/your-domain.com/public_html
sudo chmod 644 .env
```

### Step 6: Create Systemd Service

```bash
sudo nano /etc/systemd/system/offerearner.service
```

Add this content:
```ini
[Unit]
Description=OfferEarner Node.js Application
After=network.target

[Service]
Type=simple
User=raour
Group=raour
WorkingDirectory=/home/raour/web/your-domain.com/public_html
Environment=NODE_ENV=production
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/node dist/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 7: Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable offerearner
sudo systemctl start offerearner
sudo systemctl status offerearner
```

### Step 8: Configure Nginx Proxy

**Using HestiaCP:**
1. Go to **Web** → **Domains** → **your-domain.com**
2. Click **Edit**
3. Go to **Proxy Support** tab
4. Set **Proxy Target** to: `http://127.0.0.1:8001`
5. Enable **Proxy Support**
6. Save changes

**Manual Nginx Configuration:**
```nginx
location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

## Option 2: Python/FastAPI Deployment

### Step 1: Navigate to Python Version

```bash
cd /home/raour/web/your-domain.com/public_html/python-version
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install common missing dependencies
pip install PyJWT
pip install pydantic[email]
pip install paypalrestsdk
pip install cryptography
```

### Step 4: Environment Configuration

```bash
# Create .env file
nano .env
```

Add this content:
```env
DATABASE_URL=sqlite:///./offerwall.db
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 5: Set Permissions

```bash
sudo chown -R raour:raour /home/raour/web/your-domain.com/public_html/python-version
sudo chmod -R 755 /home/raour/web/your-domain.com/public_html/python-version
```

### Step 6: Create Systemd Service

```bash
sudo nano /etc/systemd/system/offerearner-python.service
```

Add this content:
```ini
[Unit]
Description=OfferEarner Python/FastAPI Application
After=network.target

[Service]
User=raour
Group=raour
WorkingDirectory=/home/raour/web/your-domain.com/public_html/python-version
Environment=PATH=/home/raour/web/your-domain.com/public_html/python-version/venv/bin
ExecStart=/home/raour/web/your-domain.com/public_html/python-version/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 7: Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable offerearner-python
sudo systemctl start offerearner-python
sudo systemctl status offerearner-python
```

### Step 8: Configure Nginx Proxy

Set proxy target to: `http://127.0.0.1:8000` (default FastAPI port)

## Option 3: Docker Deployment

This deployment method uses Docker containers for easy setup and isolation, ideal for production environments with external networking via Nginx Proxy Manager.

### Prerequisites for Docker

- Ubuntu VPS with Docker and Docker Compose installed
- External docker network `proxy_net` created
- Nginx Proxy Manager configured for reverse proxy and SSL

### Step 1: Install Docker and Docker Compose

```bash
# Install Docker
sudo apt update
sudo apt install docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 2: Create External Network

```bash
# Create the external network for Nginx Proxy Manager integration
docker network create proxy_net
```

### Step 3: Deploy Application

```bash
# Clone the repository
git clone https://github.com/your-username/OfferEarner-kilocode.git
cd OfferEarner-kilocode

# Copy and configure environment file
cp .env.example .env
nano .env  # Edit with your production settings

# Start the container in detached mode
docker-compose up -d

# Verify container is running
docker-compose ps
```

### Step 4: Configure Nginx Proxy Manager

1. **Access Nginx Proxy Manager** web interface
2. **Add a new Proxy Host**
3. **Domain Names**: Enter your domain or subdomain
4. **Forward Hostname / IP**: `offerearner-app` (container name)
5. **Forward Port**: `8001`
6. **Enable SSL**: Use Let's Encrypt for automatic SSL certificates
7. **Force HTTPS**: Enable for security
8. **Save** the configuration

### Step 5: Verify Deployment

```bash
# Check container status
docker-compose ps

# View application logs
docker-compose logs offerearner

# Test health endpoint (from within the network)
docker-compose exec offerearner curl -f http://localhost:8001/health

# Test through domain (after NPM configuration)
curl https://your-domain.com
```

### Docker-Specific Troubleshooting

**Container Not Starting:**
```bash
# Check logs for errors
docker-compose logs

# Rebuild and start
docker-compose up -d --build
```

**Network Issues:**
```bash
# Verify network exists
docker network ls | grep proxy_net

# Inspect network details
docker network inspect proxy_net
```

**Volume Permissions:**
```bash
# Ensure data directory has proper permissions
sudo chown -R 1000:1000 ./data  # Node.js user in container
```

## Common Configuration

### SSL Setup

**For HestiaCP Deployment:**
1. Go to **Web** → **Domains** → **your-domain.com**
2. Click **SSL** tab
3. Click **Let's Encrypt** to install SSL certificate
4. Enable **Force HTTPS** for security

**For Docker Deployment (Nginx Proxy Manager):**
- SSL is handled automatically by Nginx Proxy Manager with Let's Encrypt
- Ensure your domain DNS points to your server IP
- NPM will provision and renew SSL certificates automatically

1. Go to **Web** → **Domains** → **your-domain.com**
2. Click **SSL** tab
3. Click **Let's Encrypt** to install SSL certificate
4. Enable **Force HTTPS** for security

### Database Initialization

Both versions will automatically create the SQLite database when first started. The database file will be created at:
- Node.js: `./offerwall.db` (root directory)
- Python: `./offerwall.db` (python-version directory)

### Testing the Application

**Traditional Deployment:**
```bash
# Test Node.js version
curl http://127.0.0.1:8001

# Test Python version
curl http://127.0.0.1:8000

# Test through domain
curl https://your-domain.com
```

**Docker Deployment:**
```bash
# Test container internally
docker-compose exec offerearner curl http://localhost:8001

# Test through Nginx proxy
curl https://your-domain.com
```

```bash
# Test Node.js version
curl http://127.0.0.1:8001

# Test Python version
curl http://127.0.0.1:8000

# Test through domain
curl https://your-domain.com
```

## Troubleshooting

### Common Issues

**Port Conflicts:**
```bash
# Check what's using a port
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :8001

# Kill process using port
sudo fuser -k 8000/tcp
sudo fuser -k 8001/tcp
```

**Permission Errors:**
```bash
sudo chown -R raour:raour /home/raour/web/your-domain.com/public_html
sudo chmod -R 755 /home/raour/web/your-domain.com/public_html
```

**Service Won't Start:**
```bash
# Check logs
sudo journalctl -u offerearner -f
sudo journalctl -u offerearner-python -f

# Test manually
cd /home/raour/web/your-domain.com/public_html
node dist/server.js

# OR for Python
cd python-version
source venv/bin/activate
python start.py
```

**Missing Dependencies:**
```bash
# Node.js: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
npm run build

# Python: Reinstall in virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### Useful Commands

**Traditional Deployment:**
```bash
# Restart services
sudo systemctl restart offerearner
sudo systemctl restart offerearner-python

# View real-time logs
sudo journalctl -u offerearner -f
sudo journalctl -u offerearner-python -f

# Check service status
sudo systemctl status offerearner
sudo systemctl status offerearner-python

# Check running processes
ps aux | grep node
ps aux | grep python
```

**Docker Deployment:**
```bash
# Restart container
docker-compose restart

# View real-time logs
docker-compose logs -f

# Check container status
docker-compose ps

# Execute commands in container
docker-compose exec offerearner npm run build  # For updates

# Stop and remove containers
docker-compose down

# Rebuild with changes
docker-compose up -d --build
```

```bash
# Restart services
sudo systemctl restart offerearner
sudo systemctl restart offerearner-python

# View real-time logs
sudo journalctl -u offerearner -f
sudo journalctl -u offerearner-python -f

# Check service status
sudo systemctl status offerearner
sudo systemctl status offerearner-python

# Check running processes
ps aux | grep node
ps aux | grep python
```

## Maintenance

### Updating the Application

**Node.js Version:**
```bash
cd /home/raour/web/your-domain.com/public_html
git pull origin main
npm install
npm run build
sudo systemctl restart offerearner
```

**Python Version:**
```bash
cd /home/raour/web/your-domain.com/public_html/python-version
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart offerearner-python
```

### Backup Procedures

**Traditional Deployment:**
```bash
# Node.js database
cp /home/raour/web/your-domain.com/public_html/offerwall.db /backup/offerwall_$(date +%Y%m%d).db

# Python database
cp /home/raour/web/your-domain.com/public_html/python-version/offerwall.db /backup/offerwall_python_$(date +%Y%m%d).db

# Node.js version
tar -czf /backup/offerearner_node_$(date +%Y%m%d).tar.gz /home/raour/web/your-domain.com/public_html/

# Python version
tar -czf /backup/offerearner_python_$(date +%Y%m%d).tar.gz /home/raour/web/your-domain.com/public_html/python-version/
```

**Docker Deployment:**
```bash
# Backup database volume
tar -czf /backup/offerearner_db_$(date +%Y%m%d).tar.gz ./data/

# Backup Docker compose files
cp docker-compose.yml /backup/
cp Dockerfile /backup/
cp .dockerignore /backup/
cp .env /backup/
```

**Backup Database:**
```bash
# Node.js database
cp /home/raour/web/your-domain.com/public_html/offerwall.db /backup/offerwall_$(date +%Y%m%d).db

# Python database
cp /home/raour/web/your-domain.com/public_html/python-version/offerwall.db /backup/offerwall_python_$(date +%Y%m%d).db
```

**Backup Entire Application:**
```bash
# Node.js version
tar -czf /backup/offerearner_node_$(date +%Y%m%d).tar.gz /home/raour/web/your-domain.com/public_html/

# Python version
tar -czf /backup/offerearner_python_$(date +%Y%m%d).tar.gz /home/raour/web/your-domain.com/public_html/python-version/
```

### Security Considerations

1. **Change default secret keys** in production environment
2. **Enable SSL/HTTPS** for all traffic
3. **Set up firewall** rules to restrict access
4. **Regularly update** Node.js/Python and dependencies
5. **Monitor logs** for suspicious activity
6. **Regular backups** of database and application files

## Performance Notes

- **Node.js Version**: Generally better performance for I/O-heavy applications, better SSL handling
- **Python Version**: Good for CPU-bound tasks, simpler deployment for Python environments
- Both versions support the same feature set and API endpoints

## Choosing Between Deployment Methods

**Choose Traditional Deployment (HestiaCP) if:**
- You prefer managing services with systemd
- You have existing HestiaCP infrastructure
- You want direct control over the runtime environment
- You're comfortable with Linux service management

**Choose Docker Deployment if:**
- You want containerized isolation for better security
- You need easy scaling and deployment
- You're using Nginx Proxy Manager for SSL and reverse proxy
- You prefer Docker-based infrastructure
- You want simplified updates and rollbacks

## Choosing Between Technology Stacks

**Choose Node.js/TypeScript if:**
- You prefer modern JavaScript/TypeScript ecosystem
- You need better performance for concurrent connections
- You want better SSL and proxy handling
- You're familiar with Node.js development

**Choose Python/FastAPI if:**
- You prefer Python development
- You have existing Python infrastructure
- You need to integrate with other Python applications
- You're more comfortable with Python debugging

---

**Last Updated:** 2025-09-16
**Version:** 3.0
**Tested On:** Ubuntu with HestiaCP and Docker
**Supported:** Both Node.js 18+ and Python 3.8+, with Docker deployment