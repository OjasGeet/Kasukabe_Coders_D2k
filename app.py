import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configure page layout and title
st.set_page_config(
    page_title="Smart Task Management Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    /* Dark theme colors */
    :root {
        --background-color: #111111;
        --secondary-bg: #1e1e1e;
        --text-color: #ffffff;
        --accent: #3498db;
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .stMetric {
        background-color: var(--secondary-bg);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    .stMarkdown {
        color: var(--text-color);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }
    
    .stButton>button {
        background-color: var(--accent);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
    }
    
    /* Activity cards */
    .activity-card {
        background-color: var(--secondary-bg);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .activity-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Chart backgrounds */
    .js-plotly-plot {
        background-color: var(--secondary-bg) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--secondary-bg);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Get the current page from URL parameters
if 'page' in st.query_params:
    st.session_state.current_page = st.query_params['page']

# Header with branding
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 2rem; color: #ffffff;'>
        📊 SMART TASK MANAGEMENT DASHBOARD
    </h1>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("facility_tasks (2).csv", encoding="ISO-8859-1")
        df.columns = df.columns.str.strip()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['date'] = df['Timestamp'].dt.date
        df['missed'] = (df['Task_Status'].str.lower() == "missed").astype(int)
        df['Hour_of_Day'] = df['Timestamp'].dt.hour
        df['Day_of_Week'] = df['Timestamp'].dt.dayofweek
        df['Weekend'] = df['Day_of_Week'].apply(lambda x: 1 if x >= 5 else 0)
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'facility_tasks (2).csv' is in the correct location.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()

if df is not None:
    # Main Dashboard Content
    if st.session_state.current_page == "Dashboard":
        # Top Row: Key Metrics with custom styling
        st.markdown("### 📈 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(df)
            total_missed = df['missed'].sum()
            risk_score = (total_missed / total_tasks) * 100 if total_tasks > 0 else 0
            st.metric(
                label="Overall Risk Score",
                value=f"{risk_score:.1f}%",
                delta=f"{risk_score:.1f}%",
                delta_color="inverse"
            )
        
        with col2:
            today_tasks = df[df['date'] == df['date'].max()]
            completed_today = len(today_tasks[today_tasks['Task_Status'] == 'Completed'])
            st.metric(
                label="Tasks Completed Today",
                value=f"{completed_today}",
                delta=f"{completed_today}",
                delta_color="normal"
            )
        
        with col3:
            missed_today = len(today_tasks[today_tasks['Task_Status'] == 'Missed'])
            st.metric(
                label="Missed Tasks Today",
                value=f"{missed_today}",
                delta=f"{missed_today}",
                delta_color="inverse"
            )
        
        with col4:
            completion_rate = (completed_today / (completed_today + missed_today) * 100) if (completed_today + missed_today) > 0 else 0
            st.metric(
                label="Completion Rate",
                value=f"{completion_rate:.1f}%",
                delta=f"{completion_rate:.1f}%",
                delta_color="normal"
            )

        # Second Row: Risk Gauge and Trend
        st.markdown("### 📊 Performance Analysis")
        col5, col6 = st.columns(2)
        
        with col5:
            st.markdown("#### Task Miss Risk Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={'text': "Current Risk Level"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'steps': [
                        {'range': [0, 30], 'color': "#4CAF50"},
                        {'range': [30, 60], 'color': "#FFC107"},
                        {'range': [60, 100], 'color': "#F44336"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score
                    }
                }
            ))
            fig_gauge.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col6:
            st.markdown("#### Daily Task Completion Trend")
            daily_trend = df.groupby("date").agg({
                'Task_Status': lambda x: (x == 'Completed').sum(),
                'missed': 'sum'
            }).reset_index()
            daily_trend.columns = ['date', 'completed', 'missed']
            
            fig_trend = px.line(daily_trend, x='date', y=['completed', 'missed'],
                               title="Task Completion vs Missed Tasks",
                               labels={'value': 'Number of Tasks', 'date': 'Date'},
                               color_discrete_sequence=['#4CAF50', '#F44336'])
            fig_trend.update_traces(mode="markers+lines")
            fig_trend.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_trend, use_container_width=True)

        # Third Row: Recent Activity and Insights
        st.markdown("### 📋 Recent Activity & Insights")
        col7, col8 = st.columns(2)
        
        with col7:
            st.markdown("#### Recent Activity")
            recent_tasks = df.sort_values('Timestamp', ascending=False).head(5)
            for _, task in recent_tasks.iterrows():
                task_type = task.get('Task_Type', 'Unnamed Task')
                task_status = task.get('Task_Status', 'Unknown Status')
                timestamp = task.get('Timestamp', pd.NaT)
                
                status_color = {
                    'Completed': '#4CAF50',
                    'Missed': '#F44336',
                    'Delayed': '#FFC107'
                }.get(task_status, '#7f8c8d')
                
                if pd.notna(timestamp):
                    st.markdown(f"""
                    <div style='padding: 10px; margin: 5px 0; border-radius: 5px; background-color: #f8f9fa;'>
                        <span style='color: {status_color};'>●</span> Task "{task_type}" {task_status} at {timestamp.strftime('%Y-%m-%d %H:%M')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='padding: 10px; margin: 5px 0; border-radius: 5px; background-color: #f8f9fa;'>
                        <span style='color: {status_color};'>●</span> Task "{task_type}" {task_status}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col8:
            st.markdown("#### Key Insights")
            # Calculate insights from the data
            peak_hour = df[df['missed'] == 1]['Hour_of_Day'].mode().iloc[0] if not df[df['missed'] == 1].empty else None
            task_types = df.groupby('Task_Type')['missed'].mean().sort_values(ascending=False) if 'Task_Type' in df.columns else pd.Series()
            high_risk_type = task_types.index[0] if not task_types.empty else "Unknown"
            
            # Calculate weekend vs weekday completion rates
            weekend_completion = df[df['Weekend'] == 1]['Task_Status'].eq('Completed').mean() * 100
            weekday_completion = df[df['Weekend'] == 0]['Task_Status'].eq('Completed').mean() * 100
            
            st.markdown(f"""
            <div style='padding: 15px; border-radius: 5px; background-color: #f8f9fa;'>
                <p style='margin: 5px 0;'><span style='color: #F44336;'>●</span> Peak missed tasks occur at {peak_hour}:00</p>
                <p style='margin: 5px 0;'><span style='color: #F44336;'>●</span> {high_risk_type} tasks have the highest risk of being missed</p>
                <p style='margin: 5px 0;'><span style='color: #4CAF50;'>●</span> Weekend tasks show {weekend_completion:.1f}% completion rate vs {weekday_completion:.1f}% for weekdays</p>
            </div>
            """, unsafe_allow_html=True)

        # Bottom Row: Action Buttons
        st.markdown("### 🛠 Quick Actions")
        col9, col10, col11 = st.columns(3)
        
        with col9:
            if st.button("📊 View Detailed Analysis"):
                st.session_state.current_page = "Visualization"
                st.query_params['page'] = "Visualization"
                st.rerun()
        
        with col10:
            if st.button("📝 Update Task Assignments"):
                st.session_state.current_page = "To-Do List"
                st.query_params['page'] = "To-Do List"
                st.rerun()
        
        with col11:
            if st.button("📥 Export Data"):
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Data",
                    data=csv,
                    file_name="facility_tasks_export.csv",
                    mime="text/csv"
                )

    elif st.session_state.current_page == "Visualization":
        # Import and run the visualization page content
        import pages.visualization
        
    elif st.session_state.current_page == "Prediction":
        # Import and run the prediction page content
        import pages.prediction
        
    elif st.session_state.current_page == "To-Do List":
        # Import and run the to-do list page content
        import pages.todo 