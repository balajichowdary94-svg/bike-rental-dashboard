import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Washington D.C. Bike Rental Dashboard", layout="wide")

# ---------------------------------------------------------
# 2. Data Loading and Preprocessing (Logic from Assignment 1)
# ---------------------------------------------------------
@st.cache_data
def load_and_prep_data():
    # Attempt to load the dataset
    # Note: Ensure "train.csv" is in the same folder as this script
    df = pd.read_csv("train.csv")
    
    # Requirement: Ensure date column is in datetime format 
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Requirement: Create columns for year, month, day of week, and hour 
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    
    # Requirement: Rename values in the season column 
    season_map = {1: 'spring', 2: 'summer', 3: 'fall', 4: 'winter'}
    df['season'] = df['season'].map(season_map)
    
    # Requirement: Create categorical 'day_period' column 
    def get_period(h):
        if h < 6: return 'night'
        elif h < 12: return 'morning'
        elif h < 18: return 'afternoon'
        else: return 'evening'
    df['day_period'] = df['hour'].apply(get_period)
    
    return df

# Main logic execution
try:
    df = load_and_prep_data()

    # ---------------------------------------------------------
    # 3. Sidebar Interactive Widgets (Requirement: at least 3) 
    # ---------------------------------------------------------
    st.sidebar.header("Dashboard Filters")
    
    # Widget 1: Year Multi-select
    years = st.sidebar.multiselect("Select Year", options=df['year'].unique(), default=df['year'].unique())
    
    # Widget 2: Season Multi-select
    seasons = st.sidebar.multiselect("Select Season(s)", options=df['season'].unique(), default=df['season'].unique())
    
    # Widget 3: Hour Range Slider
    hour_range = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))

    # Apply filters based on widget selection
    filtered_df = df[
        (df['year'].isin(years)) & 
        (df['season'].isin(seasons)) & 
        (df['hour'].between(hour_range[0], hour_range[1]))
    ]

    # ---------------------------------------------------------
    # 4. Main Dashboard Header
    # ---------------------------------------------------------
    st.title("🚲 Washington D.C. Bike Rental Dashboard")
    st.markdown("### Interactive analysis of bike rentals based on temporal and weather factors.")
    
    # Quick Summary Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Rentals", f"{filtered_df['count'].sum():,}")
    m2.metric("Avg Hourly Rentals", round(filtered_df['count'].mean(), 2))
    m3.metric("Max Rentals in an Hour", filtered_df['count'].max())

    # ---------------------------------------------------------
    # 5. Visualizations (Requirement: 4-6 plots) 
    # ---------------------------------------------------------
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        # Plot 1: Monthly Trends (Assignment 2.4/2.5) 
        st.subheader("Monthly Rental Trends")
        monthly_avg = filtered_df.groupby(['year', 'month'])['count'].mean().reset_index()
        fig1 = px.line(monthly_avg, x='month', y='count', color='year', markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        # Plot 2: Rentals by Day Period (Assignment 2.10) 
        st.subheader("Rentals by Day Period")
        fig2 = px.box(filtered_df, x='day_period', y='count', color='workingday',
                      category_orders={"day_period": ["morning", "afternoon", "evening", "night"]})
        st.plotly_chart(fig2, use_container_width=True)

    with row1_col2:
        # Plot 3: Hourly Usage by Weekday (Assignment 2.8) 
        st.subheader("Hourly Usage by Weekday")
        hourly_avg = filtered_df.groupby(['hour', 'day_of_week'])['count'].mean().reset_index()
        fig3 = px.line(hourly_avg, x='hour', y='count', color='day_of_week')
        st.plotly_chart(fig3, use_container_width=True)

        # Plot 4: Correlation Heatmap (Assignment 2.11) 
        # Fix: Filter numeric types to avoid errors [cite: 1]
        st.subheader("Variable Correlation Heatmap")
        corr = filtered_df.select_dtypes(include=[np.number]).corr()
        fig4, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig4)

    # Plot 5: Weather Impact (Assignment 2.6) 
    st.subheader("Average Rentals by Weather Condition")
    weather_avg = filtered_df.groupby('weather')['count'].mean().reset_index()
    fig5 = px.bar(weather_avg, x='weather', y='count', color='weather', labels={'count': 'Mean Rentals'})
    st.plotly_chart(fig5, use_container_width=True)

except FileNotFoundError:
    st.error("Dataset 'train.csv' not found. Please upload the file to the app directory.")
