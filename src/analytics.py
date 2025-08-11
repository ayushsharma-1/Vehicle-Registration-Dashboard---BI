"""
Advanced Analytics Module for Vehicle Registration Data

This module provides sophisticated analytics capabilities for investment
decision-making, including market concentration analysis, volatility metrics,
correlation studies, and investment scoring algorithms.

Key Features:
- CAGR (Compound Annual Growth Rate) calculations
- Market concentration analysis (HHI scores)
- Volatility and risk-adjusted return metrics
- Investment scoring and ranking algorithms
- Seasonal trend analysis and pattern recognition
- Correlation analysis between manufacturers and categories

Classes:
    VehicleAnalytics: Main analytics engine with comprehensive reporting

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
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class VehicleAnalytics:
    """Advanced analytics for vehicle registration data"""
    
    def __init__(self, database_path=DATABASE_PATH):
        self.db_path = database_path
        self.conn = sqlite3.connect(database_path)
    
    def load_data_by_period(self, start_date, end_date):
        """Load data for specific period"""
        query = """
        SELECT * FROM vehicle_registrations
        WHERE date BETWEEN ? AND ?
        ORDER BY date, vehicle_category, manufacturer
        """
        df = pd.read_sql(query, self.conn, params=(start_date, end_date))
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def calculate_cagr(self, df, years):
        """Calculate Compound Annual Growth Rate"""
        if len(df) < 2 or years <= 0:
            return None
        
        start_value = df.iloc[0]['registrations']
        end_value = df.iloc[-1]['registrations']
        
        if start_value <= 0:
            return None
            
        cagr = ((end_value / start_value) ** (1/years)) - 1
        return round(cagr * 100, 2)
    
    def seasonal_analysis(self, df):
        """Analyze seasonal trends in vehicle registrations"""
        monthly_avg = df.groupby('month')['registrations'].mean()
        
        # Calculate seasonality index (month average / overall average)
        overall_avg = df['registrations'].mean()
        seasonality_index = (monthly_avg / overall_avg).round(3)
        
        seasonal_insights = {
            'monthly_averages': monthly_avg.to_dict(),
            'seasonality_index': seasonality_index.to_dict(),
            'peak_month': seasonality_index.idxmax(),
            'low_month': seasonality_index.idxmin(),
            'seasonal_variation': round((seasonality_index.max() - seasonality_index.min()) * 100, 1)
        }
        
        return seasonal_insights
    
    def market_concentration_analysis(self, df):
        """Calculate market concentration metrics (HHI, CR4, etc.)"""
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        concentration_metrics = {}
        
        for category in latest_data['vehicle_category'].unique():
            cat_data = latest_data[latest_data['vehicle_category'] == category]
            
            # Calculate market shares
            total_registrations = cat_data['registrations'].sum()
            market_shares = (cat_data['registrations'] / total_registrations * 100).sort_values(ascending=False)
            
            # Herfindahl-Hirschman Index
            hhi = (market_shares ** 2).sum()
            
            # Concentration Ratio (CR4 - top 4 firms)
            cr4 = market_shares.head(4).sum()
            
            concentration_metrics[category] = {
                'hhi': round(hhi, 2),
                'cr4': round(cr4, 2),
                'top_players': market_shares.head(5).to_dict(),
                'market_structure': self._classify_market_structure(hhi)
            }
        
        return concentration_metrics
    
    def _classify_market_structure(self, hhi):
        """Classify market structure based on HHI"""
        if hhi < 1500:
            return "Competitive"
        elif hhi < 2500:
            return "Moderately Concentrated"
        else:
            return "Highly Concentrated"
    
    def growth_volatility_analysis(self, df):
        """Analyze growth volatility for investment risk assessment"""
        volatility_metrics = {}
        
        for category in df['vehicle_category'].unique():
            cat_data = df[df['vehicle_category'] == category].copy()
            cat_data = cat_data.sort_values('date')
            
            # Calculate monthly growth rates
            cat_data['monthly_growth'] = cat_data.groupby('manufacturer')['registrations'].pct_change() * 100
            
            # Volatility metrics per manufacturer
            mfr_volatility = cat_data.groupby('manufacturer')['monthly_growth'].agg([
                'std', 'mean', 'min', 'max'
            ]).round(2)
            
            # Risk-adjusted returns (Sharpe-like ratio)
            mfr_volatility['risk_adjusted_return'] = (mfr_volatility['mean'] / mfr_volatility['std']).round(2)
            
            volatility_metrics[category] = mfr_volatility.to_dict('index')
        
        return volatility_metrics
    
    def correlation_analysis(self, df):
        """Analyze correlations between different manufacturers and categories"""
        # Pivot data for correlation analysis
        pivot_df = df.pivot_table(
            index='date',
            columns=['vehicle_category', 'manufacturer'],
            values='registrations',
            fill_value=0
        )
        
        # Calculate correlation matrix
        correlation_matrix = pivot_df.corr()
        
        # Find highest correlations (excluding self-correlations)
        correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                if not pd.isna(corr_value):
                    correlations.append({
                        'pair': f"{col1} - {col2}",
                        'correlation': round(corr_value, 3)
                    })
        
        # Sort by absolute correlation value
        correlations = sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'correlation_matrix': correlation_matrix.round(3),
            'top_correlations': correlations[:10],
            'high_correlations': [c for c in correlations if abs(c['correlation']) > 0.7]
        }
    
    def investment_scoring(self, df):
        """Create investment scoring for manufacturers"""
        latest_date = df['date'].max()
        one_year_ago = latest_date - timedelta(days=365)
        
        # Get last 12 months data
        recent_data = df[df['date'] > one_year_ago].copy()
        
        scoring_metrics = {}
        
        for category in recent_data['vehicle_category'].unique():
            cat_data = recent_data[recent_data['vehicle_category'] == category]
            
            manufacturer_scores = {}
            
            for manufacturer in cat_data['manufacturer'].unique():
                mfr_data = cat_data[cat_data['manufacturer'] == manufacturer].copy()
                mfr_data = mfr_data.sort_values('date')
                
                if len(mfr_data) < 3:  # Need minimum data points
                    continue
                
                # Calculate metrics
                latest_registrations = mfr_data.iloc[-1]['registrations']
                avg_registrations = mfr_data['registrations'].mean()
                
                # Growth metrics
                growth_rates = mfr_data['registrations'].pct_change().dropna()
                avg_growth = growth_rates.mean() * 100
                growth_volatility = growth_rates.std() * 100
                
                # Market share (approximate)
                total_category = cat_data.groupby('date')['registrations'].sum()
                mfr_share = (mfr_data.set_index('date')['registrations'] / total_category * 100).mean()
                
                # Calculate scores (0-100 scale)
                growth_score = min(max((avg_growth + 10) * 5, 0), 100)  # -10% to +10% mapped to 0-100
                size_score = min((latest_registrations / avg_registrations) * 50, 100)
                stability_score = max(100 - growth_volatility * 2, 0)
                market_position_score = min(mfr_share * 10, 100)
                
                # Combined score with weights
                combined_score = (
                    growth_score * 0.3 +
                    size_score * 0.25 +
                    stability_score * 0.25 +
                    market_position_score * 0.2
                )
                
                manufacturer_scores[manufacturer] = {
                    'combined_score': round(combined_score, 1),
                    'growth_score': round(growth_score, 1),
                    'size_score': round(size_score, 1),
                    'stability_score': round(stability_score, 1),
                    'market_position_score': round(market_position_score, 1),
                    'avg_growth': round(avg_growth, 2),
                    'growth_volatility': round(growth_volatility, 2),
                    'market_share': round(mfr_share, 2),
                    'latest_registrations': int(latest_registrations)
                }
            
            # Sort by combined score
            scoring_metrics[category] = dict(
                sorted(manufacturer_scores.items(), 
                      key=lambda x: x[1]['combined_score'], 
                      reverse=True)
            )
        
        return scoring_metrics
    
    def trend_classification(self, df):
        """Classify trends as bullish, bearish, or sideways"""
        trend_analysis = {}
        
        for category in df['vehicle_category'].unique():
            cat_data = df[df['vehicle_category'] == category].copy()
            
            # Aggregate by month
            monthly_data = cat_data.groupby(['year', 'month'])['registrations'].sum().reset_index()
            monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))
            monthly_data = monthly_data.sort_values('date')
            
            if len(monthly_data) < 6:  # Need minimum data points
                continue
            
            # Calculate trend metrics
            recent_6m = monthly_data.tail(6)['registrations'].mean()
            previous_6m = monthly_data.head(len(monthly_data)-6).tail(6)['registrations'].mean()
            
            # Linear trend
            x = range(len(monthly_data))
            y = monthly_data['registrations'].values
            trend_slope = np.polyfit(x, y, 1)[0]
            
            # Classify trend
            if recent_6m > previous_6m * 1.1 and trend_slope > 0:
                trend = "Bullish"
            elif recent_6m < previous_6m * 0.9 and trend_slope < 0:
                trend = "Bearish"
            else:
                trend = "Sideways"
            
            trend_analysis[category] = {
                'trend': trend,
                'recent_6m_avg': int(recent_6m),
                'previous_6m_avg': int(previous_6m),
                'change_percent': round((recent_6m - previous_6m) / previous_6m * 100, 2),
                'trend_slope': round(trend_slope, 2)
            }
        
        return trend_analysis
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analytics report"""
        # Load all data
        df = pd.read_sql("SELECT * FROM vehicle_registrations ORDER BY date", self.conn)
        if df.empty:
            return None
            
        df['date'] = pd.to_datetime(df['date'])
        
        report = {
            'data_summary': {
                'total_records': len(df),
                'date_range': f"{df['date'].min().strftime('%Y-%m')} to {df['date'].max().strftime('%Y-%m')}",
                'categories': df['vehicle_category'].unique().tolist(),
                'manufacturers': df['manufacturer'].nunique(),
                'total_registrations': int(df['registrations'].sum())
            },
            'seasonal_analysis': self.seasonal_analysis(df),
            'market_concentration': self.market_concentration_analysis(df),
            'volatility_analysis': self.growth_volatility_analysis(df),
            'investment_scoring': self.investment_scoring(df),
            'trend_classification': self.trend_classification(df),
            'correlation_analysis': self.correlation_analysis(df)
        }
        
        return report
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Test the analytics module"""
    analytics = VehicleAnalytics()
    
    print("Generating comprehensive analytics report...")
    report = analytics.generate_comprehensive_report()
    
    if report:
        print(f"\nData Summary:")
        print(f"Total records: {report['data_summary']['total_records']:,}")
        print(f"Date range: {report['data_summary']['date_range']}")
        print(f"Categories: {', '.join(report['data_summary']['categories'])}")
        
        print(f"\nSeasonal Analysis:")
        seasonal = report['seasonal_analysis']
        print(f"Peak month: {seasonal['peak_month']}")
        print(f"Low month: {seasonal['low_month']}")
        print(f"Seasonal variation: {seasonal['seasonal_variation']}%")
        
        print(f"\nTrend Classification:")
        for category, trend in report['trend_classification'].items():
            print(f"{category}: {trend['trend']} ({trend['change_percent']:+.1f}%)")
    else:
        print("No data available for analysis")

if __name__ == "__main__":
    main()
