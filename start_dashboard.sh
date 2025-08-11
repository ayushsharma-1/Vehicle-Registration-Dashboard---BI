#!/bin/bash

# Vehicle Registration Dashboard - Production Startup Script
# Professional-grade launcher with comprehensive environment setup
# Version: 1.0.0
# Date: August 11, 2025

set -e  # Exit on any error

# Color codes for professional output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}🚗 Vehicle Registration Dashboard - Investment Intelligence${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python version
echo "🔍 Checking system requirements..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python 3.8+ required but not found"
    exit 1
fi

# Setup virtual environment
if [ ! -d ".venv" ]; then
    print_warning "Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment"
source .venv/bin/activate

# Install/update dependencies
if [ ! -f ".venv/pyvenv.cfg" ] || [ requirements.txt -nt .venv/pyvenv.cfg ]; then
    print_warning "Installing/updating dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    print_status "Dependencies installed successfully"
else
    print_status "Dependencies up to date"
fi

# Initialize database if needed
if [ ! -f "data/vehicle_data.db" ]; then
    print_warning "Initializing database with sample data..."
    mkdir -p data/raw data/processed
    python src/data_collection.py
    python src/data_processing.py
    print_status "Database initialized with sample data"
else
    print_status "Database found and ready"
fi

# System health check
echo ""
echo "🔧 Running system health check..."
python -c "
import sys, os
sys.path.extend(['src', 'config'])
try:
    from config.settings import *
    from src.data_processing import DataProcessor
    print('✅ All modules imported successfully')
    
    # Quick data validation
    import sqlite3
    conn = sqlite3.connect('data/vehicle_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM vehicle_registrations')
    count = cursor.fetchone()[0]
    conn.close()
    print(f'✅ Database contains {count:,} records')
    
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "System health check passed"
else
    print_error "System health check failed"
    exit 1
fi

# Launch dashboard
echo ""
echo -e "${BLUE}🌐 Launching Investment Dashboard...${NC}"
echo -e "${YELLOW}📊 Dashboard Features:${NC}"
echo "   • Interactive time series analysis"
echo "   • YoY/QoQ growth calculations" 
echo "   • Investment scoring and recommendations"
echo "   • Market concentration analysis"
echo "   • Professional data export"
echo ""
echo -e "${GREEN}🔗 Access URLs:${NC}"
echo "   • Local:    http://localhost:8501"
echo "   • Network:  http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   • Use Ctrl+C to stop the server"
echo "   • Refresh browser if connection issues occur"  
echo "   • Check logs for any error messages"
echo ""
echo -e "${BLUE}================================================================${NC}"

# Launch Streamlit with optimized settings
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

streamlit run dashboard.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.base light
