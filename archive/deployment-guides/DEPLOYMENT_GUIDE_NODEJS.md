# OfferEarner Node.js Deployment Guide

This guide covers deploying the TypeScript/Node.js version of OfferEarner to your VPS with HestiaCP.

## Prerequisites

- SSH access to your VPS
- Node.js 18+ installed on your VPS
- Git access to your repository
- HestiaCP access for domain management

## Step 1: Clean Up Previous FastAPI Installation

### Stop and Remove FastAPI Service
```bash
# SSH into your VPS
ssh ubuntu@your-server-ip

# Stop the FastAPI service
sudo systemctl stop offerearner
sudo systemctl disable offerearner

# Remove the service file
sudo rm /etc/systemd/system/offerearner.service

# Reload systemd
sudo systemctl daemon-reload
```

### Clean Up Python Environment
```bash
# Navigate to your project directory
cd /home/raour/web/offerearner.raour.site/public_html

# Remove the Python virtual environment
rm -rf venv

# Remove Python-specific files
rm -f requirements.txt
rm -f start.py
rm -f run.sh
```

## Step 2: Install Node.js and npm

### Check if Node.js is already installed
```bash
node --version
npm --version
```

### If Node.js is not installed, install it:
```bash
# Update package list
sudo apt update

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

## Step 3: Deploy the New Application

### Clone/Pull Latest Code
```bash
# Navigate to your project directory
cd /home/raour/web/offerearner.raour.site/public_html

# If you have a Git repository, pull the latest changes
git pull origin main

# Or if you need to clone fresh
# git clone https://github.com/your-username/offerearner.git .
```

### Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Install TypeScript globally (if needed)
sudo npm install -g typescript
```

### Build the Application
```bash
# Build the TypeScript application
npm run build
```

### Set Up Environment Variables
```bash
# Create .env file
nano .env
```

Add the following content to `.env`:
```env
# Database Configuration
DATABASE_URL=sqlite:./offerwall.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
PORT=8001
NODE_ENV=production

# PayPal Configuration (optional)
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=sandbox

# Lootably Configuration (optional)
LOOTABLY_API_KEY=your-lootably-api-key
LOOTABLY_SECRET_KEY=your-lootably-secret-key
```

### Set Proper Permissions
```bash
# Set ownership to raour user
sudo chown -R raour:raour /home/raour/web/offerearner.raour.site/public_html

# Set proper permissions
sudo chmod -R 755 /home/raour/web/offerearner.raour.site/public_html
sudo chmod 644 /home/raour/web/offerearner.raour.site/public_html/.env
```

## Step 4: Create Systemd Service

### Create the service file
```bash
sudo nano /etc/systemd/system/offerearner.service
```

Add the following content:
```ini
[Unit]
Description=OfferEarner Node.js Application
After=network.target

[Service]
Type=simple
User=raour
Group=raour
WorkingDirectory=/home/raour/web/offerearner.raour.site/public_html
Environment=NODE_ENV=production
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/node dist/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start the Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable offerearner

# Start the service
sudo systemctl start offerearner

# Check status
sudo systemctl status offerearner
```

## Step 5: Configure Nginx (HestiaCP)

### Update Nginx Configuration
In HestiaCP, go to your domain settings and update the proxy configuration:

1. Go to **Web** → **Domains** → **offerearner.raour.site**
2. Click **Edit** next to the domain
3. Go to **Proxy Support** tab
4. Set **Proxy Target** to: `http://127.0.0.1:8001`
5. Enable **Proxy Support**
6. Save changes

### Alternative: Direct Nginx Configuration
If you need to edit the Nginx config directly:

```bash
sudo nano /home/raour/conf/web/offerearner.raour.site/nginx.conf
```

Add this inside the `server` block:
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

## Step 6: Test the Application

### Check if the application is running
```bash
# Check service status
sudo systemctl status offerearner

# Check if the port is listening
sudo netstat -tlnp | grep 8001

# Test the application directly
curl http://127.0.0.1:8001
```

### Check logs if there are issues
```bash
# Check service logs
sudo journalctl -u offerearner -f

# Check application logs
tail -f /home/raour/web/offerearner.raour.site/public_html/logs/app.log
```

## Step 7: SSL Configuration (Optional)

### Using HestiaCP SSL
1. Go to **Web** → **Domains** → **offerearner.raour.site**
2. Click **SSL** tab
3. Click **Let's Encrypt** to install SSL certificate
4. Enable **Force HTTPS** if desired

### Using Cloudflare
1. Set DNS to Cloudflare
2. Enable **Proxy** (orange cloud)
3. Set SSL/TLS mode to **Full**
4. Enable **Always Use HTTPS**

## Step 8: Database Setup

### Initialize the Database
```bash
# Navigate to your project directory
cd /home/raour/web/offerearner.raour.site/public_html

# The database will be created automatically when the app starts
# But you can also run it manually to check for errors
node dist/server.js
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :8001
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   sudo chown -R raour:raour /home/raour/web/offerearner.raour.site/public_html
   sudo chmod -R 755 /home/raour/web/offerearner.raour.site/public_html
   ```

3. **Node.js not found**
   ```bash
   which node
   # If not found, reinstall Node.js
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

4. **Build errors**
   ```bash
   # Clean and reinstall
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

5. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u offerearner -f
   
   # Test manually
   cd /home/raour/web/offerearner.raour.site/public_html
   node dist/server.js
   ```

### Useful Commands

```bash
# Restart the service
sudo systemctl restart offerearner

# View real-time logs
sudo journalctl -u offerearner -f

# Check if port is in use
sudo netstat -tlnp | grep 8001

# Check process
ps aux | grep node

# Test the application
curl -I http://127.0.0.1:8001
```

## Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
npm install

# Build the application
npm run build

# Restart the service
sudo systemctl restart offerearner
```

### Backup Database
```bash
# Backup SQLite database
cp /home/raour/web/offerearner.raour.site/public_html/offerwall.db /home/raour/web/offerearner.raour.site/public_html/offerwall.db.backup
```

## Security Notes

1. Change the `SECRET_KEY` in production
2. Use strong passwords for database
3. Keep Node.js and npm updated
4. Regularly backup your database
5. Monitor logs for suspicious activity

## Performance Optimization

1. Use PM2 for process management (optional)
2. Enable Nginx caching
3. Use CDN for static assets
4. Monitor memory usage

This deployment should resolve the SSL issues you experienced with FastAPI, as Node.js/Express handles SSL and proxy configurations much more reliably.
