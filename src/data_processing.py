"""
Vehicle Registration Data Processing Module

This module processes raw vehicle registration data to calculate key metrics
and prepare it for analysis and visualization in the dashboard.

Key Functions:
- Calculate YoY (Year-over-Year) and QoQ (Quarter-over-Quarter) growth rates
- Aggregate data by categories and manufacturers
- Compute market share percentages
- Generate rolling averages and trends
- Create investment insights and summaries

Classes:
    DataProcessor: Main class for data processing operations

Author: Ayush Sharma
Date: August 11, 2025
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class DataProcessor:
    """Class to process and clean vehicle registration data"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
    
    def load_data(self):
        """Load data from database"""
        query = """
        SELECT * FROM vehicle_registrations
        ORDER BY date, vehicle_category, manufacturer
        """
        df = pd.read_sql(query, self.conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def calculate_growth_metrics(self, df):
        """Calculate YoY and QoQ growth metrics"""
        
        # Sort data
        df = df.sort_values(['vehicle_category', 'manufacturer', 'date'])
        
        # Calculate YoY growth
        df['registrations_yoy'] = df.groupby(['vehicle_category', 'manufacturer'])['registrations'].shift(12)
        df['yoy_growth'] = ((df['registrations'] - df['registrations_yoy']) / df['registrations_yoy'] * 100).round(2)
        
        # Calculate QoQ growth  
        df['registrations_qoq'] = df.groupby(['vehicle_category', 'manufacturer'])['registrations'].shift(3)
        df['qoq_growth'] = ((df['registrations'] - df['registrations_qoq']) / df['registrations_qoq'] * 100).round(2)
        
        # Calculate rolling averages
        df['registrations_3m_avg'] = df.groupby(['vehicle_category', 'manufacturer'])['registrations'].transform(lambda x: x.rolling(3).mean())
        df['registrations_12m_avg'] = df.groupby(['vehicle_category', 'manufacturer'])['registrations'].transform(lambda x: x.rolling(12).mean())
        
        return df
    
    def aggregate_category_data(self, df):
        """Aggregate data by vehicle category"""
        
        category_df = df.groupby(['date', 'year', 'month', 'quarter', 'vehicle_category']).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Calculate growth metrics for categories
        category_df = category_df.sort_values(['vehicle_category', 'date'])
        
        category_df['registrations_yoy'] = category_df.groupby('vehicle_category')['registrations'].shift(12)
        category_df['yoy_growth'] = ((category_df['registrations'] - category_df['registrations_yoy']) / category_df['registrations_yoy'] * 100).round(2)
        
        category_df['registrations_qoq'] = category_df.groupby('vehicle_category')['registrations'].shift(3)
        category_df['qoq_growth'] = ((category_df['registrations'] - category_df['registrations_qoq']) / category_df['registrations_qoq'] * 100).round(2)
        
        return category_df
    
    def aggregate_manufacturer_data(self, df):
        """Aggregate data by manufacturer"""
        
        mfr_df = df.groupby(['date', 'year', 'month', 'quarter', 'vehicle_category', 'manufacturer']).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Calculate market share
        total_by_category = mfr_df.groupby(['date', 'vehicle_category'])['registrations'].sum().reset_index()
        total_by_category.rename(columns={'registrations': 'total_category_registrations'}, inplace=True)
        
        mfr_df = mfr_df.merge(total_by_category, on=['date', 'vehicle_category'])
        mfr_df['market_share'] = (mfr_df['registrations'] / mfr_df['total_category_registrations'] * 100).round(2)
        
        # Calculate growth metrics
        mfr_df = mfr_df.sort_values(['vehicle_category', 'manufacturer', 'date'])
        
        mfr_df['registrations_yoy'] = mfr_df.groupby(['vehicle_category', 'manufacturer'])['registrations'].shift(12)
        mfr_df['yoy_growth'] = ((mfr_df['registrations'] - mfr_df['registrations_yoy']) / mfr_df['registrations_yoy'] * 100).round(2)
        
        mfr_df['registrations_qoq'] = mfr_df.groupby(['vehicle_category', 'manufacturer'])['registrations'].shift(3)
        mfr_df['qoq_growth'] = ((mfr_df['registrations'] - mfr_df['registrations_qoq']) / mfr_df['registrations_qoq'] * 100).round(2)
        
        return mfr_df
    
    def calculate_investment_insights(self, df):
        """Calculate key investment insights"""
        
        insights = {}
        
        # Latest month data
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        # Growth leaders by category
        insights['growth_leaders'] = {}
        for category in VEHICLE_CATEGORIES.keys():
            cat_data = latest_data[latest_data['vehicle_category'] == category]
            if not cat_data.empty:
                growth_leader = cat_data.loc[cat_data['yoy_growth'].idxmax()]
                insights['growth_leaders'][category] = {
                    'manufacturer': growth_leader['manufacturer'],
                    'yoy_growth': growth_leader['yoy_growth'],
                    'registrations': growth_leader['registrations'],
                    'market_share': growth_leader.get('market_share', 0)
                }
        
        # Market leaders by registrations
        insights['market_leaders'] = {}
        for category in VEHICLE_CATEGORIES.keys():
            cat_data = latest_data[latest_data['vehicle_category'] == category]
            if not cat_data.empty:
                market_leader = cat_data.loc[cat_data['registrations'].idxmax()]
                insights['market_leaders'][category] = {
                    'manufacturer': market_leader['manufacturer'],
                    'registrations': market_leader['registrations'],
                    'market_share': market_leader.get('market_share', 0),
                    'yoy_growth': market_leader['yoy_growth']
                }
        
        # Overall trends
        category_totals = latest_data.groupby('vehicle_category')['registrations'].sum()
        insights['category_distribution'] = category_totals.to_dict()
        
        # Total market size
        insights['total_registrations'] = latest_data['registrations'].sum()
        
        return insights
    
    def process_all_data(self):
        """Main processing function"""
        print("Loading data from database...")
        df = self.load_data()
        
        if df.empty:
            print("No data found in database. Please run data collection first.")
            return None, None, None
        
        print(f"Processing {len(df)} records...")
        
        # Calculate growth metrics
        df = self.calculate_growth_metrics(df)
        
        # Create aggregated views
        category_data = self.aggregate_category_data(df)
        manufacturer_data = self.aggregate_manufacturer_data(df)
        
        # Calculate investment insights
        insights = self.calculate_investment_insights(manufacturer_data)
        
        # Save processed data
        processed_file = os.path.join(PROCESSED_DATA_DIR, f"processed_data_{datetime.now().strftime('%Y%m%d')}.csv")
        df.to_csv(processed_file, index=False)
        
        category_file = os.path.join(PROCESSED_DATA_DIR, f"category_data_{datetime.now().strftime('%Y%m%d')}.csv")
        category_data.to_csv(category_file, index=False)
        
        manufacturer_file = os.path.join(PROCESSED_DATA_DIR, f"manufacturer_data_{datetime.now().strftime('%Y%m%d')}.csv")
        manufacturer_data.to_csv(manufacturer_file, index=False)
        
        print("Data processing completed!")
        print(f"Total records processed: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Categories: {df['vehicle_category'].unique()}")
        print(f"Manufacturers: {df['manufacturer'].nunique()}")
        
        return df, category_data, manufacturer_data, insights
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main execution function"""
    processor = DataProcessor()
    df, category_data, manufacturer_data, insights = processor.process_all_data()
    
    if df is not None:
        print("\nKey Insights:")
        print(f"Total registrations in latest month: {insights['total_registrations']:,}")
        print("\nGrowth Leaders:")
        for category, data in insights['growth_leaders'].items():
            print(f"{category}: {data['manufacturer']} ({data['yoy_growth']:.1f}% YoY growth)")

if __name__ == "__main__":
    main()
