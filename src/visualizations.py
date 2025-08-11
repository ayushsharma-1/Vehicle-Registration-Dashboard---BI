"""
Interactive Visualization Module for Vehicle Registration Dashboard

This module creates professional, interactive visualizations using Plotly
for comprehensive analysis of vehicle registration data with investor focus.

Visualization Types:
- Time series charts with trend analysis
- Growth rate visualizations (YoY/QoQ)
- Market share pie charts and comparisons
- Manufacturer performance bar charts
- Seasonal heatmaps and pattern analysis
- Risk-return scatter plots
- Investment scoring visualizations
- Multi-category comparison dashboards

Classes:
    VehicleVisualizations: Main visualization engine with chart generation methods

Author: Ayush Sharma
Date: August 11, 2025
Version: 1.0.0
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import COLOR_PALETTE, VEHICLE_CATEGORIES

class VehicleVisualizations:
    """Class for creating vehicle registration visualizations"""
    
    def __init__(self):
        self.colors = COLOR_PALETTE
    
    def create_time_series_chart(self, df, title="Vehicle Registrations Over Time"):
        """Create time series chart for vehicle registrations"""
        
        fig = px.line(
            df, 
            x='date', 
            y='registrations',
            color='vehicle_category',
            title=title,
            color_discrete_map={
                '2W': self.colors['2W'],
                '3W': self.colors['3W'], 
                '4W': self.colors['4W']
            }
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Registrations",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_growth_chart(self, df, growth_type='yoy_growth'):
        """Create growth chart (YoY or QoQ)"""
        
        title = "Year-over-Year Growth" if growth_type == 'yoy_growth' else "Quarter-over-Quarter Growth"
        
        fig = px.line(
            df,
            x='date',
            y=growth_type,
            color='vehicle_category',
            title=title,
            color_discrete_map={
                '2W': self.colors['2W'],
                '3W': self.colors['3W'],
                '4W': self.colors['4W']
            }
        )
        
        # Add horizontal line at 0%
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Growth Rate (%)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_manufacturer_comparison(self, df, category='2W', top_n=10):
        """Create manufacturer comparison chart"""
        
        # Filter by category and get latest data
        latest_date = df['date'].max()
        category_data = df[
            (df['vehicle_category'] == category) & 
            (df['date'] == latest_date)
        ].nlargest(top_n, 'registrations')
        
        fig = px.bar(
            category_data,
            x='registrations',
            y='manufacturer',
            orientation='h',
            title=f"Top {top_n} {VEHICLE_CATEGORIES[category]} Manufacturers",
            color='registrations',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Registrations",
            yaxis_title="Manufacturer",
            template='plotly_white'
        )
        
        return fig
    
    def create_market_share_pie(self, df, category='2W', date=None):
        """Create market share pie chart"""
        
        if date is None:
            date = df['date'].max()
        
        category_data = df[
            (df['vehicle_category'] == category) & 
            (df['date'] == date)
        ]
        
        # Get top manufacturers and group others
        top_manufacturers = category_data.nlargest(8, 'registrations')
        others_sum = category_data[~category_data['manufacturer'].isin(top_manufacturers['manufacturer'])]['registrations'].sum()
        
        if others_sum > 0:
            others_row = pd.DataFrame({
                'manufacturer': ['Others'],
                'registrations': [others_sum]
            })
            plot_data = pd.concat([top_manufacturers[['manufacturer', 'registrations']], others_row])
        else:
            plot_data = top_manufacturers[['manufacturer', 'registrations']]
        
        fig = px.pie(
            plot_data,
            values='registrations',
            names='manufacturer',
            title=f"{VEHICLE_CATEGORIES[category]} Market Share ({date.strftime('%Y-%m')})"
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        return fig
    
    def create_seasonal_heatmap(self, df):
        """Create seasonal heatmap showing registrations by month and year"""
        
        # Aggregate data by year and month
        seasonal_data = df.groupby(['year', 'month', 'vehicle_category'])['registrations'].sum().reset_index()
        
        figs = []
        for category in seasonal_data['vehicle_category'].unique():
            cat_data = seasonal_data[seasonal_data['vehicle_category'] == category]
            
            # Pivot data for heatmap
            pivot_data = cat_data.pivot_table(
                index='month',
                columns='year', 
                values='registrations',
                fill_value=0
            )
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=[f"Month {i}" for i in pivot_data.index],
                colorscale='Blues',
                showscale=True
            ))
            
            fig.update_layout(
                title=f"Seasonal Pattern - {VEHICLE_CATEGORIES[category]}",
                xaxis_title="Year",
                yaxis_title="Month",
                template='plotly_white'
            )
            
            figs.append(fig)
        
        return figs
    
    def create_growth_vs_share_scatter(self, df, category='2W'):
        """Create scatter plot of growth vs market share"""
        
        latest_date = df['date'].max()
        category_data = df[
            (df['vehicle_category'] == category) & 
            (df['date'] == latest_date)
        ].copy()
        
        if category_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for selected filters",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False
            )
            fig.update_layout(
                title=f"Growth vs Market Share - {VEHICLE_CATEGORIES[category]}",
                template='plotly_white'
            )
            return fig
        
        # Calculate market share if not available
        if 'market_share' not in category_data.columns:
            total_registrations = category_data['registrations'].sum()
            category_data['market_share'] = (category_data['registrations'] / total_registrations * 100).round(2)
        
        # Filter out rows with missing yoy_growth data
        category_data = category_data.dropna(subset=['yoy_growth'])
        
        if category_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No growth data available for selected category",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False
            )
            fig.update_layout(
                title=f"Growth vs Market Share - {VEHICLE_CATEGORIES[category]}",
                template='plotly_white'
            )
            return fig
        
        fig = px.scatter(
            category_data,
            x='market_share',
            y='yoy_growth',
            size='registrations',
            hover_name='manufacturer',
            title=f"Growth vs Market Share - {VEHICLE_CATEGORIES[category]}",
            color='yoy_growth',
            color_continuous_scale='RdYlGn'
        )
        
        # Add quadrant lines
        if len(category_data) > 1:
            fig.add_hline(y=category_data['yoy_growth'].median(), line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=category_data['market_share'].median(), line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            xaxis_title="Market Share (%)",
            yaxis_title="YoY Growth (%)",
            template='plotly_white'
        )
        
        return fig
    
    def create_multi_category_comparison(self, df):
        """Create comparison chart across all categories"""
        
        # Aggregate by category and date
        category_totals = df.groupby(['date', 'vehicle_category'])['registrations'].sum().reset_index()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Registrations', 'YoY Growth', 'Market Share Distribution', 'Trend Analysis'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "pie"}, {"secondary_y": False}]]
        )
        
        # Time series plot
        for category in category_totals['vehicle_category'].unique():
            cat_data = category_totals[category_totals['vehicle_category'] == category]
            fig.add_trace(
                go.Scatter(
                    x=cat_data['date'],
                    y=cat_data['registrations'],
                    name=category,
                    line=dict(color=self.colors[category])
                ),
                row=1, col=1
            )
        
        # Calculate and add growth rates
        category_totals_sorted = category_totals.sort_values(['vehicle_category', 'date'])
        category_totals_sorted['yoy_growth'] = category_totals_sorted.groupby('vehicle_category')['registrations'].pct_change(12) * 100
        
        for category in category_totals_sorted['vehicle_category'].unique():
            cat_data = category_totals_sorted[category_totals_sorted['vehicle_category'] == category]
            fig.add_trace(
                go.Scatter(
                    x=cat_data['date'],
                    y=cat_data['yoy_growth'],
                    name=category,
                    line=dict(color=self.colors[category]),
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Market share pie
        latest_totals = category_totals[category_totals['date'] == category_totals['date'].max()]
        fig.add_trace(
            go.Pie(
                values=latest_totals['registrations'],
                labels=latest_totals['vehicle_category'],
                marker_colors=[self.colors[cat] for cat in latest_totals['vehicle_category']]
            ),
            row=2, col=1
        )
        
        # Trend indicators (simplified)
        trend_data = category_totals.groupby('vehicle_category')['registrations'].last()
        fig.add_trace(
            go.Bar(
                x=trend_data.index,
                y=trend_data.values,
                marker_color=[self.colors[cat] for cat in trend_data.index],
                showlegend=False
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Vehicle Registration Dashboard Overview",
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def create_investment_scoring_chart(self, scoring_data, category='2W'):
        """Create investment scoring visualization"""
        
        if category not in scoring_data:
            return None
        
        manufacturers = list(scoring_data[category].keys())[:10]  # Top 10
        scores = [scoring_data[category][mfr]['combined_score'] for mfr in manufacturers]
        
        fig = go.Figure(data=go.Bar(
            x=scores,
            y=manufacturers,
            orientation='h',
            marker_color=px.colors.sequential.Blues_r,
            text=[f"{score:.1f}" for score in scores],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f"Investment Scoring - {VEHICLE_CATEGORIES[category]}",
            xaxis_title="Investment Score (0-100)",
            yaxis_title="Manufacturer",
            template='plotly_white'
        )
        
        return fig
    
    def create_volatility_vs_return_chart(self, volatility_data, category='2W'):
        """Create risk-return scatter plot"""
        
        if category not in volatility_data:
            return None
        
        manufacturers = []
        returns = []
        risks = []
        
        for mfr, data in volatility_data[category].items():
            if not pd.isna(data['mean']) and not pd.isna(data['std']):
                manufacturers.append(mfr)
                returns.append(data['mean'])
                risks.append(data['std'])
        
        fig = px.scatter(
            x=risks,
            y=returns,
            text=manufacturers,
            title=f"Risk vs Return - {VEHICLE_CATEGORIES[category]}",
            labels={'x': 'Risk (Volatility %)', 'y': 'Average Monthly Growth (%)'}
        )
        
        fig.update_traces(textposition="top center")
        fig.update_layout(template='plotly_white')
        
        return fig

def main():
    """Test visualization functions"""
    # This would normally load real data
    print("Visualization module ready!")
    print("Available visualization functions:")
    print("- create_time_series_chart")
    print("- create_growth_chart") 
    print("- create_manufacturer_comparison")
    print("- create_market_share_pie")
    print("- create_seasonal_heatmap")
    print("- create_growth_vs_share_scatter")
    print("- create_multi_category_comparison")
    print("- create_investment_scoring_chart")
    print("- create_volatility_vs_return_chart")

if __name__ == "__main__":
    main()
