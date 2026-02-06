#!/bin/bash

# setup.sh - Environment Setup for Key Finder

echo "========================================="
echo "   Key Finder - Setup Wizard"
echo "========================================="

# 1. Virtual Environment Setup
echo "[*] Checking Python Virtual Environment..."
if [ ! -d "venv" ]; then
    echo "    Creating virtual environment..."
    python3 -m venv venv
else
    echo "    Virtual environment exists."
fi

# Activate venv
source venv/bin/activate

# 2. Install Dependencies
echo "[*] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi
echo "    Dependencies installed."

# 3. Configuration Setup (.env)
if [ ! -f ".env" ]; then
    echo "[*] Creating .env configuration file..."
    cp .env.example .env
    
    echo "    Please enter your configuration details below."
    echo "    (Press Enter to keep blank/default if unsure)"
    echo ""
    
    read -p "Telegram API ID: " api_id
    if [ ! -z "$api_id" ]; then
        sed -i "s/TELEGRAM_API_ID=/TELEGRAM_API_ID=$api_id/" .env
    fi
    
    read -p "Telegram API Hash: " api_hash
    if [ ! -z "$api_hash" ]; then
        sed -i "s/TELEGRAM_API_HASH=/TELEGRAM_API_HASH=$api_hash/" .env
    fi

    read -p "Google Drive Folder IDs (comma separated): " folder_ids
    if [ ! -z "$folder_ids" ]; then
        sed -i "s/GDRIVE_FOLDER_IDS=/GDRIVE_FOLDER_IDS=$folder_ids/" .env
    fi

    echo ""
    echo "[+] .env file created."
else
    echo "[*] .env file already exists. Skipping configuration."
fi

echo ""
echo "========================================="
echo "   Setup Complete!"
echo "========================================="
echo "To run the application, execute: ./launch.sh"
echo "Make sure you have your 'client_secrets.json' file if you use Google Drive upload."
