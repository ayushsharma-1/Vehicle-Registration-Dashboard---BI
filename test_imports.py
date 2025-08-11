"""
Test script to check if all imports work correctly
"""

print("Testing imports...")

try:
    import streamlit as st
    print("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Streamlit import failed: {e}")

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
except ImportError as e:
    print(f"❌ Pandas import failed: {e}")

try:
    import plotly.express as px
    print("✅ Plotly imported successfully")
except ImportError as e:
    print(f"❌ Plotly import failed: {e}")

try:
    import sqlite3
    print("✅ SQLite imported successfully")
except ImportError as e:
    print(f"❌ SQLite import failed: {e}")

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
    
    from config.settings import *
    print("✅ Config settings imported successfully")
except ImportError as e:
    print(f"❌ Config import failed: {e}")

try:
    from src.data_processing import DataProcessor
    print("✅ DataProcessor imported successfully")
except ImportError as e:
    print(f"❌ DataProcessor import failed: {e}")

try:
    from src.analytics import VehicleAnalytics
    print("✅ VehicleAnalytics imported successfully") 
except ImportError as e:
    print(f"❌ VehicleAnalytics import failed: {e}")

try:
    from src.visualizations import VehicleVisualizations
    print("✅ VehicleVisualizations imported successfully")
except ImportError as e:
    print(f"❌ VehicleVisualizations import failed: {e}")

print("\nAll imports tested!")
