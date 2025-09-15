# SUPER SIMPLE Deployment Guide

This guide will get your TypeScript site working in 10 minutes. No complex stuff.

## Step 1: Clean Up (2 minutes)

SSH into your server and run these commands:

```bash
# Stop the old FastAPI service
sudo systemctl stop offerearner
sudo systemctl disable offerearner

# Go to your website folder
cd /home/raour/web/offerearner.raour.site/public_html

# Delete old Python files (keep the new TypeScript files)
rm -f main.py start.py run.sh requirements.txt
rm -rf venv __pycache__ templates static
```

## Step 2: Install Node.js (3 minutes)

```bash
# Install Node.js (copy and paste this entire block)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Check if it worked
node --version
npm --version
```

## Step 3: Install Your Website (2 minutes)

```bash
# Go to your website folder
cd /home/raour/web/offerearner.raour.site/public_html

# Install the website
npm install

# Build the website
npm run build
```

## Step 4: Create the .env file (1 minute)

```bash
# Create the config file
nano .env
```

Copy and paste this into the file:
```env
DATABASE_URL=sqlite:./offerwall.db
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8001
NODE_ENV=production
```

Save the file (Ctrl+X, then Y, then Enter)

## Step 5: Create the Service (2 minutes)

```bash
# Create the service file
sudo nano /etc/systemd/system/offerearner.service
```

Copy and paste this into the file:
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
ExecStart=/usr/bin/node dist/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save the file (Ctrl+X, then Y, then Enter)

## Step 6: Start the Website (1 minute)

```bash
# Start the service
sudo systemctl daemon-reload
sudo systemctl enable offerearner
sudo systemctl start offerearner

# Check if it's working
sudo systemctl status offerearner
```

## Step 7: Update Nginx (1 minute)

In HestiaCP:
1. Go to **Web** → **Domains** → **offerearner.raour.site**
2. Click **Edit**
3. Go to **Proxy Support** tab
4. Set **Proxy Target** to: `http://127.0.0.1:8001`
5. Enable **Proxy Support**
6. Click **Save**

## Step 8: Test It

Visit your website: `http://offerearner.raour.site`

## If Something Goes Wrong

### Check if the service is running:
```bash
sudo systemctl status offerearner
```

### Check the logs:
```bash
sudo journalctl -u offerearner -f
```

### Test the website directly:
```bash
cd /home/raour/web/offerearner.raour.site/public_html
node dist/server.js
```

### If you get permission errors:
```bash
sudo chown -R raour:raour /home/raour/web/offerearner.raour.site/public_html
```

## That's It!

Your website should now be working. The TypeScript version handles SSL much better than FastAPI, so you shouldn't have the SSL issues anymore.

If you want to add SSL later, just go to HestiaCP → **Web** → **Domains** → **offerearner.raour.site** → **SSL** tab and click **Let's Encrypt**.
