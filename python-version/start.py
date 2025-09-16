#!/usr/bin/env python3
"""
Startup script for OfferEarner application
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"Starting OfferEarner on {host}:{port}")
    print(f"Reload mode: {reload}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        # Handle HTTPS behind Cloudflare
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
