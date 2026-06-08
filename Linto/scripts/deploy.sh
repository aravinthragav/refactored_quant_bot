#!/bin/bash
# ==============================================================================
# Auto-Deployment Script for AI Gold Forecast Terminal (GitHub Webhook Trigger)
# ==============================================================================

echo "=== Deployment started at $(date) ==="

# Navigate to the repo directory
REPO_DIR="/home/ubuntu/refactored_quant_bot"
if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR" || exit 1
else
    echo "Directory $REPO_DIR does not exist. Aborting."
    exit 1
fi

# Pull latest changes from main branch
echo "Pulling latest changes from Git..."
git pull origin main

# Build the Next.js Frontend
echo "Building the Next.js Frontend..."
cd Linto/frontend || exit 1

# Install dependency updates if package.json changed
npm install

# Run production build
npm run build

# Restart PM2 process
echo "Restarting PM2 Frontend instance..."
pm2 restart gold-frontend

# Restart PM2 Backend/Quant Engine processes
echo "Restarting PM2 Backend & Quant Engine instances..."
pm2 restart gold-api
pm2 restart gold-bot

echo "=== Deployment finished successfully at $(date) ==="
