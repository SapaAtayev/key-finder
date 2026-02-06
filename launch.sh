#!/bin/bash

# launch.sh - Main Execution Script

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check for .env
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Check for venv
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found."
    exit 1
fi

echo "Starting Key Finder..."
python3 main.py
