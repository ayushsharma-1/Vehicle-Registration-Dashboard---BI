"""
Vehicle Registration Data Collection Module

This module handles the collection and generation of vehicle registration data
for the dashboard. It includes both real-world scraping capabilities (for future
implementation) and sample data generation for demonstration purposes.

Classes:
    VahanDataCollector: Main class for data collection and database management

Functions:
    - create_database(): Initialize SQLite database with proper schema
    - generate_sample_data(): Create realistic sample data for demonstration
    - scrape_vahan_data(): Placeholder for actual data scraping (future)
    - save_to_database(): Store collected data in database

Author: Ayush Sharma
Date: August 11, 2025
Version: 1.0.0
"""

import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VahanDataCollector:
    """Class to collect vehicle registration data from Vahan Dashboard"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
    def create_database(self):
        """Create SQLite database and tables"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Create registrations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    year INTEGER,
                    month INTEGER,
                    quarter INTEGER,
                    state TEXT,
                    rto TEXT,
                    vehicle_category TEXT,
                    vehicle_class TEXT,
                    manufacturer TEXT,
                    registrations INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON vehicle_registrations(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON vehicle_registrations(vehicle_category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manufacturer ON vehicle_registrations(manufacturer)')
            
            conn.commit()
            conn.close()
            logger.info("Database created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            
    def generate_sample_data(self):
        """Generate sample data for development when scraping is not available"""
        logger.info("Generating sample data...")
        
        np.random.seed(42)  # For reproducible results
        
        data = []
        
        # Generate data for last 5 years
        for year in range(START_YEAR, END_YEAR + 1):
            for month in range(1, 13):
                for category in VEHICLE_CATEGORIES.keys():
                    for manufacturer in MAJOR_MANUFACTURERS[category][:5]:  # Top 5 per category
                        
                        # Base registration numbers with trends
                        base_registrations = {
                            "2W": 50000,
                            "3W": 5000,
                            "4W": 30000
                        }
                        
                        # Add growth trends
                        growth_factor = 1 + (year - START_YEAR) * 0.05  # 5% annual growth
                        seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * month / 12)  # Seasonal variation
                        
                        # Random manufacturer market share
                        mfr_factor = np.random.uniform(0.1, 0.3)
                        
                        registrations = int(
                            base_registrations[category] * 
                            growth_factor * 
                            seasonal_factor * 
                            mfr_factor * 
                            np.random.uniform(0.8, 1.2)  # Random variation
                        )
                        
                        data.append({
                            'date': datetime(year, month, 1),
                            'year': year,
                            'month': month,
                            'quarter': (month - 1) // 3 + 1,
                            'state': 'ALL',
                            'rto': 'ALL',
                            'vehicle_category': category,
                            'vehicle_class': VEHICLE_CLASSES[category][0],
                            'manufacturer': manufacturer,
                            'registrations': registrations
                        })
        
        # Save to database
        self.save_to_database(data)
        logger.info(f"Generated {len(data)} sample records")
        
        return data
    
    def scrape_vahan_data(self, year=None):
        """Scrape data from Vahan dashboard"""
        if year is None:
            year = CURRENT_YEAR
            
        logger.info(f"Scraping data for year {year}")
        
        try:
            # This is a simplified version - actual implementation would need
            # to handle the complex JavaScript forms and AJAX requests
            response = self.session.get(VAHAN_REPORT_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse table data - this would need to be adapted based on actual HTML structure
            data = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        # Extract data based on table structure
                        # This is a placeholder implementation
                        pass
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping data: {e}")
            return []
    
    def save_to_database(self, data):
        """Save data to SQLite database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.DataFrame(data)
            
            # Insert data into database
            df.to_sql('vehicle_registrations', conn, if_exists='append', index=False)
            
            conn.close()
            logger.info(f"Saved {len(data)} records to database")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def collect_all_data(self):
        """Main method to collect all data"""
        logger.info("Starting data collection...")
        
        # Create database
        self.create_database()
        
        # For now, use sample data since actual scraping requires handling complex forms
        if SAMPLE_DATA_ENABLED:
            data = self.generate_sample_data()
        else:
            data = []
            for year in range(START_YEAR, END_YEAR + 1):
                year_data = self.scrape_vahan_data(year)
                data.extend(year_data)
                time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        
        # Save raw data as JSON for backup
        raw_file = os.path.join(RAW_DATA_DIR, f"raw_data_{datetime.now().strftime('%Y%m%d')}.json")
        with open(raw_file, 'w') as f:
            json.dump(data, f, default=str, indent=2)
        
        logger.info("Data collection completed!")
        return data

def main():
    """Main execution function"""
    collector = VahanDataCollector()
    data = collector.collect_all_data()
    print(f"Collected {len(data)} records")
    print("Data collection completed! You can now run the dashboard.")

if __name__ == "__main__":
    main()
