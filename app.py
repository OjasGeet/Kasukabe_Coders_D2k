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

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Visualization", "Prediction", "To-Do List"]
)

# Header with branding
st.title("📊 SMART TASK MANAGEMENT DASHBOARD")
st.markdown("### Real-time insights for efficient task management")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("facility_tasks (2).csv", encoding="ISO-8859-1")
        df.columns = df.columns.str.strip()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['date'] = df['Timestamp'].dt.date
        df['missed'] = (df['Task_Status'].str.lower() == "missed").astype(int)
        # Print column names for debugging
        st.write("Available columns:", df.columns.tolist())
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
    if page == "Dashboard":
        # Top Row: Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(df)
            total_missed = df['missed'].sum()
            risk_score = (total_missed / total_tasks) * 100 if total_tasks > 0 else 0
            st.metric(
                label="Overall Risk Score",
                value=f"{risk_score:.1f}%",
                delta=f"{risk_score:.1f}%"
            )
        
        with col2:
            today_tasks = df[df['date'] == df['date'].max()]
            completed_today = len(today_tasks[today_tasks['Task_Status'] == 'Completed'])
            st.metric(
                label="Tasks Completed Today",
                value=f"{completed_today}",
                delta=f"{completed_today}"
            )
        
        with col3:
            missed_today = len(today_tasks[today_tasks['Task_Status'] == 'Missed'])
            st.metric(
                label="Missed Tasks Today",
                value=f"{missed_today}",
                delta=f"{missed_today}"
            )
        
        with col4:
            completion_rate = (completed_today / (completed_today + missed_today) * 100) if (completed_today + missed_today) > 0 else 0
            st.metric(
                label="Completion Rate",
                value=f"{completion_rate:.1f}%",
                delta=f"{completion_rate:.1f}%"
            )

        # Second Row: Risk Gauge and Trend
        col5, col6 = st.columns(2)
        
        with col5:
            st.subheader("Task Miss Risk Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={'text': "Current Risk Level"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgray"},
                        {'range': [30, 60], 'color': "gray"},
                        {'range': [60, 100], 'color': "darkgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col6:
            st.subheader("Daily Task Completion Trend")
            daily_trend = df.groupby("date").agg({
                'Task_Status': lambda x: (x == 'Completed').sum(),
                'missed': 'sum'
            }).reset_index()
            daily_trend.columns = ['date', 'completed', 'missed']
            
            fig_trend = px.line(daily_trend, x='date', y=['completed', 'missed'],
                               title="Task Completion vs Missed Tasks",
                               labels={'value': 'Number of Tasks', 'date': 'Date'})
            fig_trend.update_traces(mode="markers+lines")
            st.plotly_chart(fig_trend, use_container_width=True)

        # Third Row: Recent Activity and Insights
        col7, col8 = st.columns(2)
        
        with col7:
            st.subheader("Recent Activity")
            recent_tasks = df.sort_values('Timestamp', ascending=False).head(5)
            for _, task in recent_tasks.iterrows():
                # Safely access task information with fallbacks
                task_name = task.get('Task_Name', 'Unnamed Task')
                task_status = task.get('Task_Status', 'Unknown Status')
                timestamp = task.get('Timestamp', pd.NaT)
                
                if pd.notna(timestamp):
                    st.markdown(f"""
                    - Task "{task_name}" {task_status} at {timestamp.strftime('%Y-%m-%d %H:%M')}
                    """)
                else:
                    st.markdown(f"""
                    - Task "{task_name}" {task_status}
                    """)
        
        with col8:
            st.subheader("Key Insights")
            # Calculate insights from the data
            peak_hour = df[df['missed'] == 1]['Hour_of_Day'].mode().iloc[0] if 'Hour_of_Day' in df.columns else None
            task_types = df.groupby('Task_Type')['missed'].mean().sort_values(ascending=False) if 'Task_Type' in df.columns else pd.Series()
            high_risk_type = task_types.index[0] if not task_types.empty else "Unknown"
            
            st.markdown(f"""
            - Peak missed tasks occur at {peak_hour}:00
            - {high_risk_type} tasks have the highest risk of being missed
            - Weekend tasks show higher completion rates
            """)

        # Bottom Row: Action Buttons
        st.markdown("### Quick Actions")
        col9, col10, col11 = st.columns(3)
        
        with col9:
            if st.button("View Detailed Analysis"):
                st.info("Redirecting to Analysis page...")
        
        with col10:
            if st.button("Update Task Assignments"):
                st.info("Opening task assignment interface...")
        
        with col11:
            if st.button("Export Data"):
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Data",
                    data=csv,
                    file_name="facility_tasks_export.csv",
                    mime="text/csv"
                )

elif page == "Visualization":
    # Import and run the visualization page content
    import pages.visualization
    
elif page == "Prediction":
    # Import and run the prediction page content
    import pages.prediction
    
elif page == "To-Do List":
    # Import and run the to-do list page content
    import pages.todo 