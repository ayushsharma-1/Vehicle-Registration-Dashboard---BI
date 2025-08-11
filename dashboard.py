"""
Vehicle Registration Dashboard - Main Application

An interactive Streamlit dashboard for analyzing Indian vehicle registration data
with a focus on providing investor insights and market intelligence.

Features:
- Interactive time series analysis
- YoY and QoQ growth calculations
- Market share and concentration analysis
- Investment scoring and recommendations
- Seasonal trend analysis
- Professional data export capabilities

Author: Ayush Sharma
Date: August 11, 2025
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.settings import *
from src.data_processing import DataProcessor
from src.analytics import VehicleAnalytics  
from src.visualizations import VehicleVisualizations

# Page configuration
st.set_page_config(**STREAMLIT_CONFIG)

class VehicleDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        self.viz = VehicleVisualizations()
        self.analytics = VehicleAnalytics()
        self.load_data()
    
    @st.cache_data
    def load_data(_self):
        """Load and cache data"""
        try:
            if not os.path.exists(DATABASE_PATH):
                st.error("Database not found. Please run data collection first.")
                st.stop()
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Load main data
            df = pd.read_sql("SELECT * FROM vehicle_registrations ORDER BY date", conn)
            if df.empty:
                st.error("No data found in database. Please run data collection first.")
                st.stop()
            
            df['date'] = pd.to_datetime(df['date'])
            
            # Process data
            processor = DataProcessor()
            processed_df, category_df, manufacturer_df, insights = processor.process_all_data()
            
            conn.close()
            
            return processed_df, category_df, manufacturer_df, insights
        
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()
    
    def render_sidebar(self):
        """Render sidebar filters"""
        st.sidebar.header("🔍 Filters & Settings")
        
        # Date range selector
        min_date = self.df['date'].min().date()
        max_date = self.df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(max_date - timedelta(days=365), max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Vehicle category filter
        categories = st.sidebar.multiselect(
            "Vehicle Categories",
            options=list(VEHICLE_CATEGORIES.keys()),
            default=list(VEHICLE_CATEGORIES.keys()),
            format_func=lambda x: f"{x} - {VEHICLE_CATEGORIES[x]}"
        )
        
        # Manufacturer filter
        available_manufacturers = sorted(self.df['manufacturer'].unique())
        manufacturers = st.sidebar.multiselect(
            "Select Manufacturers",
            options=available_manufacturers,
            default=available_manufacturers[:10] if len(available_manufacturers) > 10 else available_manufacturers
        )
        
        # Metric selector
        metric_type = st.sidebar.selectbox(
            "Primary Metric",
            ["Registrations", "YoY Growth", "QoQ Growth", "Market Share"]
        )
        
        return date_range, categories, manufacturers, metric_type
    
    def render_key_metrics(self, filtered_df):
        """Render key metrics cards"""
        st.header("📊 Key Performance Indicators")
        
        # Calculate metrics
        latest_month = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
        total_registrations = latest_month['registrations'].sum()
        
        # Previous month for comparison
        prev_month_date = filtered_df['date'].max() - timedelta(days=30)
        prev_month = filtered_df[filtered_df['date'] <= prev_month_date]
        if not prev_month.empty:
            prev_month = prev_month[prev_month['date'] == prev_month['date'].max()]
            prev_total = prev_month['registrations'].sum()
            mom_growth = ((total_registrations - prev_total) / prev_total * 100) if prev_total > 0 else 0
        else:
            mom_growth = 0
        
        # Average YoY growth
        avg_yoy = latest_month['yoy_growth'].mean()
        
        # Market leader
        market_leader = latest_month.loc[latest_month['registrations'].idxmax()]
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Registrations",
                f"{total_registrations:,}",
                f"{mom_growth:+.1f}% MoM"
            )
        
        with col2:
            st.metric(
                "Avg YoY Growth",
                f"{avg_yoy:.1f}%",
                "Overall trend"
            )
        
        with col3:
            st.metric(
                "Market Leader",
                market_leader['manufacturer'],
                f"{market_leader['registrations']:,} units"
            )
        
        with col4:
            active_manufacturers = len(latest_month)
            st.metric(
                "Active Manufacturers",
                active_manufacturers,
                "Tracked brands"
            )
    
    def render_trend_analysis(self, filtered_df, category_df):
        """Render trend analysis section"""
        st.header("📈 Trend Analysis")
        
        # Time series chart
        st.subheader("Registration Trends Over Time")
        time_series_fig = self.viz.create_time_series_chart(
            category_df,
            "Vehicle Registrations Over Time"
        )
        st.plotly_chart(time_series_fig, use_container_width=True)
        
        # Growth charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Year-over-Year Growth")
            yoy_fig = self.viz.create_growth_chart(category_df, 'yoy_growth')
            st.plotly_chart(yoy_fig, use_container_width=True)
        
        with col2:
            st.subheader("Quarter-over-Quarter Growth")
            qoq_fig = self.viz.create_growth_chart(category_df, 'qoq_growth')
            st.plotly_chart(qoq_fig, use_container_width=True)
    
    def render_manufacturer_analysis(self, filtered_df):
        """Render manufacturer analysis section"""
        st.header("🏭 Manufacturer Analysis")
        
        # Category selector for detailed analysis
        selected_category = st.selectbox(
            "Select Category for Detailed Analysis",
            options=list(VEHICLE_CATEGORIES.keys()),
            format_func=lambda x: f"{x} - {VEHICLE_CATEGORIES[x]}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"Top Manufacturers - {VEHICLE_CATEGORIES[selected_category]}")
            mfr_fig = self.viz.create_manufacturer_comparison(filtered_df, selected_category)
            st.plotly_chart(mfr_fig, use_container_width=True)
        
        with col2:
            st.subheader(f"Market Share - {VEHICLE_CATEGORIES[selected_category]}")
            pie_fig = self.viz.create_market_share_pie(filtered_df, selected_category)
            st.plotly_chart(pie_fig, use_container_width=True)
        
        # Growth vs Market Share analysis
        st.subheader("Growth vs Market Share Analysis")
        scatter_fig = self.viz.create_growth_vs_share_scatter(filtered_df, selected_category)
        st.plotly_chart(scatter_fig, use_container_width=True)
    
    def render_investment_insights(self, filtered_df):
        """Render investment insights section"""
        st.header("💡 Investment Insights")
        
        # Generate analytics report
        report = self.analytics.generate_comprehensive_report()
        
        if report:
            # Investment scoring
            st.subheader("Investment Scoring")
            
            scoring_category = st.selectbox(
                "Select Category for Investment Scoring",
                options=list(VEHICLE_CATEGORIES.keys()),
                format_func=lambda x: f"{x} - {VEHICLE_CATEGORIES[x]}",
                key="investment_scoring_category"
            )
            
            if 'investment_scoring' in report and scoring_category in report['investment_scoring']:
                scoring_fig = self.viz.create_investment_scoring_chart(
                    report['investment_scoring'], 
                    scoring_category
                )
                st.plotly_chart(scoring_fig, use_container_width=True)
                
                # Top performers table
                st.subheader("Top Investment Opportunities")
                scoring_data = report['investment_scoring'][scoring_category]
                top_performers = list(scoring_data.items())[:5]
                
                for i, (manufacturer, metrics) in enumerate(top_performers, 1):
                    with st.expander(f"{i}. {manufacturer} (Score: {metrics['combined_score']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Growth Score", f"{metrics['growth_score']:.1f}")
                            st.metric("Avg Growth", f"{metrics['avg_growth']:.1f}%")
                        
                        with col2:
                            st.metric("Stability Score", f"{metrics['stability_score']:.1f}")
                            st.metric("Volatility", f"{metrics['growth_volatility']:.1f}%")
                        
                        with col3:
                            st.metric("Market Share", f"{metrics['market_share']:.1f}%")
                            st.metric("Latest Registrations", f"{metrics['latest_registrations']:,}")
            
            # Market concentration analysis
            st.subheader("Market Concentration Analysis")
            
            if 'market_concentration' in report:
                conc_data = []
                for category, metrics in report['market_concentration'].items():
                    conc_data.append({
                        'Category': VEHICLE_CATEGORIES[category],
                        'HHI Score': metrics['hhi'],
                        'CR4 Ratio': f"{metrics['cr4']:.1f}%",
                        'Market Structure': metrics['market_structure']
                    })
                
                conc_df = pd.DataFrame(conc_data)
                st.dataframe(conc_df, use_container_width=True)
            
            # Trend classification
            st.subheader("Market Trend Classification")
            
            if 'trend_classification' in report:
                trend_data = []
                for category, trend_info in report['trend_classification'].items():
                    trend_data.append({
                        'Category': VEHICLE_CATEGORIES[category],
                        'Trend': trend_info['trend'],
                        'Change (6M)': f"{trend_info['change_percent']:+.1f}%",
                        'Current Avg': f"{trend_info['recent_6m_avg']:,}",
                        'Previous Avg': f"{trend_info['previous_6m_avg']:,}"
                    })
                
                trend_df = pd.DataFrame(trend_data)
                st.dataframe(trend_df, use_container_width=True)
    
    def render_seasonal_analysis(self, filtered_df):
        """Render seasonal analysis section"""
        st.header("📅 Seasonal Analysis")
        
        # Generate report for seasonal data
        report = self.analytics.generate_comprehensive_report()
        
        if report and 'seasonal_analysis' in report:
            seasonal_data = report['seasonal_analysis']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Seasonal Insights")
                st.metric("Peak Month", f"Month {seasonal_data['peak_month']}")
                st.metric("Low Month", f"Month {seasonal_data['low_month']}")
                st.metric("Seasonal Variation", f"{seasonal_data['seasonal_variation']}%")
            
            with col2:
                st.subheader("Monthly Seasonality Index")
                monthly_data = pd.DataFrame(
                    list(seasonal_data['seasonality_index'].items()),
                    columns=['Month', 'Seasonality Index']
                )
                st.bar_chart(monthly_data.set_index('Month'))
        
        # Heatmap visualizations
        st.subheader("Seasonal Heatmaps")
        heatmap_figs = self.viz.create_seasonal_heatmap(filtered_df)
        
        for fig in heatmap_figs:
            st.plotly_chart(fig, use_container_width=True)
    
    def render_export_section(self, filtered_df):
        """Render data export section"""
        st.header("📤 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Download Filtered Data"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"vehicle_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Generate Summary Report"):
                summary = f"""
                Vehicle Registration Analysis Report
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                
                Data Overview:
                - Records: {len(filtered_df):,}
                - Date Range: {filtered_df['date'].min().strftime('%Y-%m')} to {filtered_df['date'].max().strftime('%Y-%m')}
                - Categories: {', '.join(filtered_df['vehicle_category'].unique())}
                - Manufacturers: {filtered_df['manufacturer'].nunique()}
                
                Key Metrics:
                - Total Registrations: {filtered_df['registrations'].sum():,}
                - Average Monthly Registrations: {filtered_df.groupby('date')['registrations'].sum().mean():,.0f}
                - Average YoY Growth: {filtered_df['yoy_growth'].mean():.1f}%
                """
                
                st.download_button(
                    label="📊 Download Report",
                    data=summary,
                    file_name=f"summary_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
        
        with col3:
            st.info("💡 **Export Tips:**\n- Filter data before export\n- Use summary for executive reports\n- CSV for detailed analysis")
    
    def run(self):
        """Main dashboard runner"""
        # Load data
        self.df, self.category_df, self.manufacturer_df, self.insights = self.load_data()
        
        # Render header
        st.title("🚗 Vehicle Registration Dashboard")
        st.markdown("### Investor Insights for Indian Automotive Market")
        
        with st.expander("ℹ️ About this Dashboard"):
            st.markdown("""
            This dashboard provides comprehensive analysis of Indian vehicle registration data with a focus on investment insights:
            
            - **Data Source**: Vahan Dashboard (Government of India)
            - **Coverage**: 2W (Two-wheeler), 3W (Three-wheeler), 4W (Four-wheeler)
            - **Metrics**: YoY/QoQ growth, market share, seasonal trends
            - **Investment Focus**: Growth opportunities, market concentration, risk analysis
            """)
        
        # Render sidebar and get filters
        date_range, categories, manufacturers, metric_type = self.render_sidebar()
        
        # Filter data based on selections
        if len(date_range) == 2:
            filtered_df = self.df[
                (self.df['date'].dt.date >= date_range[0]) &
                (self.df['date'].dt.date <= date_range[1])
            ]
        else:
            filtered_df = self.df
        
        if categories:
            filtered_df = filtered_df[filtered_df['vehicle_category'].isin(categories)]
            filtered_category_df = self.category_df[self.category_df['vehicle_category'].isin(categories)]
        else:
            filtered_category_df = self.category_df
        
        if manufacturers:
            filtered_df = filtered_df[filtered_df['manufacturer'].isin(manufacturers)]
        
        # Render dashboard sections
        if not filtered_df.empty:
            self.render_key_metrics(filtered_df)
            
            # Main content tabs
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📈 Trends", "🏭 Manufacturers", "💡 Investment", 
                "📅 Seasonal", "🔍 Analytics", "📤 Export"
            ])
            
            with tab1:
                self.render_trend_analysis(filtered_df, filtered_category_df)
            
            with tab2:
                self.render_manufacturer_analysis(filtered_df)
            
            with tab3:
                self.render_investment_insights(filtered_df)
            
            with tab4:
                self.render_seasonal_analysis(filtered_df)
            
            with tab5:
                st.subheader("📊 Advanced Analytics")
                
                # Multi-category overview
                overview_fig = self.viz.create_multi_category_comparison(filtered_df)
                st.plotly_chart(overview_fig, use_container_width=True)
                
                # Detailed data table
                st.subheader("📋 Detailed Data")
                st.dataframe(
                    filtered_df.sort_values('date', ascending=False).head(1000),
                    use_container_width=True
                )
            
            with tab6:
                self.render_export_section(filtered_df)
        
        else:
            st.warning("No data available for the selected filters. Please adjust your selection.")
        
        # Footer
        st.markdown("---")
        st.markdown(
            "📊 **Vehicle Registration Dashboard** | "
            "Data source: Vahan Dashboard | "
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

def main():
    """Main application entry point"""
    try:
        dashboard = VehicleDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please ensure you have run the data collection script first: `python src/data_collection.py`")

if __name__ == "__main__":
    main()
