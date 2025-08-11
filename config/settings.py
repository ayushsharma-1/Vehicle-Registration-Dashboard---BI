"""
Configuration Settings for Vehicle Registration Dashboard

This module contains all configuration parameters, constants, and settings
used across the vehicle registration dashboard application.

Categories:
- Data source URLs and endpoints
- File paths and directory structure
- Vehicle categorization and classification
- Visualization and color schemes
- Application constants and thresholds

Author: Ayush Sharma
Date: August 11, 2025
Version: 1.0.0
"""

import os
from datetime import datetime, timedelta

# Base URLs
VAHAN_BASE_URL = "https://vahan.parivahan.gov.in/vahan4dashboard"
VAHAN_REPORT_URL = f"{VAHAN_BASE_URL}/vahan/view/reportview.xhtml"
VAHAN_DASHBOARD_URL = f"{VAHAN_BASE_URL}/vahan/dashboardview.xhtml"

# Data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
DATABASE_PATH = os.path.join(DATA_DIR, "vehicle_data.db")

# Vehicle categories
VEHICLE_CATEGORIES = {
    "2W": "Two Wheeler",
    "3W": "Three Wheeler", 
    "4W": "Four Wheeler"
}

# Vehicle classes mapping
VEHICLE_CLASSES = {
    "2W": ["MOTOR CYCLE", "MOPED", "SCOOTER"],
    "3W": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)"],
    "4W": ["MOTOR CAR", "MOTOR CAR(LMV)", "GOODS VEHICLE", "BUS", "TAXI"]
}

# Major manufacturers to track
MAJOR_MANUFACTURERS = {
    "2W": [
        "HERO MOTOCORP", "HONDA", "TVS", "BAJAJ", "YAMAHA", 
        "SUZUKI", "ROYAL ENFIELD", "KTM", "MAHINDRA"
    ],
    "3W": [
        "BAJAJ", "TVS", "MAHINDRA", "PIAGGIO", "FORCE",
        "ATUL AUTO", "KINETIC"
    ],
    "4W": [
        "MARUTI SUZUKI", "HYUNDAI", "TATA", "MAHINDRA", "HONDA",
        "TOYOTA", "FORD", "VOLKSWAGEN", "SKODA", "RENAULT",
        "NISSAN", "CHEVROLET", "BMW", "MERCEDES", "AUDI"
    ]
}

# Date ranges
CURRENT_YEAR = datetime.now().year
START_YEAR = 2019  # 5 years of historical data
END_YEAR = CURRENT_YEAR

# API headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    "page_title": "Vehicle Registration Dashboard - Investor Insights",
    "page_icon": "🚗",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Chart colors
COLOR_PALETTE = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "tertiary": "#2ca02c",
    "quaternary": "#d62728",
    "2W": "#FF6B6B",
    "3W": "#4ECDC4", 
    "4W": "#45B7D1"
}

# Growth thresholds for investor insights
GROWTH_THRESHOLDS = {
    "high_growth": 20,    # 20%+ growth
    "moderate_growth": 10, # 10-20% growth
    "low_growth": 5,      # 5-10% growth
    "decline": 0          # Below 5% or negative
}

# Database tables
DB_TABLES = {
    "registrations": "vehicle_registrations",
    "manufacturers": "manufacturer_data", 
    "categories": "category_wise_data",
    "regional": "regional_data"
}

# Sample data for development (when scraping is not available)
SAMPLE_DATA_ENABLED = True

# Rate limiting for web scraping
RATE_LIMIT_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# Data validation rules
DATA_VALIDATION = {
    "min_year": 2015,
    "max_year": CURRENT_YEAR + 1,
    "required_columns": ["year", "month", "category", "registrations"],
    "numeric_columns": ["registrations", "year", "month"]
}
