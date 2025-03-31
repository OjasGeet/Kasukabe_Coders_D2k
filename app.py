import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configure page layout and title
st.set_page_config(
    page_title="Task360",
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
        --card-bg: #2d2d2d;
        --text-color: #ffffff;
        --accent: #3498db;
        --success: #2ecc71;
        --warning: #f1c40f;
        --danger: #e74c3c;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--background-color) !important;
        color: var(--text-color);
    }

    /* Fix for white header strip */
    .stApp > header {
        background-color: var(--background-color) !important;
    }

    /* Fix for deployment bar */
    [data-testid="stToolbar"] {
        background-color: var(--background-color) !important;
        right: 0;
        top: 0;
        position: fixed;
        z-index: 999990;
    }

    [data-testid="stDecoration"] {
        background-color: var(--background-color) !important;
        height: 0 !important;
    }

    [data-testid="stHeader"] {
        background-color: var(--background-color) !important;
        height: 0 !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, header[data-testid="stHeader"] {
        display: none !important;
    }

    footer {
        display: none !important;
    }

    /* Remove padding at the top */
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem;
    }

    /* Sidebar/Drawer Styling */
    .css-1d391kg, .css-1p05t8e {
        background-color: var(--card-bg) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--card-bg);
        border-right: 1px solid #333333;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-color);
    }

    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent;
        border-color: #333333;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSelectbox span {
        color: var(--text-color) !important;
    }

    /* Sidebar Radio Buttons */
    .st-cc, .st-cd, .st-ce, .st-bd, .st-be, .st-bf {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
    }

    .st-c0 {
        background-color: var(--accent) !important;
    }

    /* Sidebar Expander */
    .css-pkbazv {
        background-color: var(--card-bg) !important;
    }

    /* Sidebar Text */
    .css-17lntkn {
        color: var(--text-color) !important;
    }

    /* Sidebar Selection */
    .css-1outpf7 {
        background-color: var(--accent) !important;
    }

    /* Metric cards */
    .stMetric {
        background-color: var(--card-bg) !important;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        border: 1px solid #333333;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Text elements */
    .stMarkdown {
        color: var(--text-color) !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: var(--text-color) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--accent);
        color: var(--text-color);
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
        background-color: #2980b9;
    }
    
    /* Activity cards */
    .activity-card {
        background-color: var(--card-bg) !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        border: 1px solid #333333;
    }
    
    .activity-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Chart backgrounds */
    .js-plotly-plot {
        background-color: var(--card-bg) !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background-color: var(--card-bg);
        color: var(--text-color);
        border-color: #333333;
    }
    
    /* Selectbox */
    .stSelectbox>div>div {
        background-color: var(--card-bg);
        color: var(--text-color);
    }
    
    /* DataFrame */
    .dataframe {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
    }
    
    .dataframe th {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
    }
    
    .dataframe td {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
    }
    
    /* Status colors */
    .status-completed { color: var(--success) !important; }
    .status-delayed { color: var(--warning) !important; }
    .status-missed { color: var(--danger) !important; }
    
    /* Custom card styles */
    .custom-card {
        background-color: var(--card-bg);
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
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
    <h1 style='
        text-align: center; 
        margin-bottom: 2rem; 
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    '>
        Task360
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
                    'Completed': 'var(--success)',
                    'Missed': 'var(--danger)',
                    'Delayed': 'var(--warning)'
                }.get(task_status, '#95a5a6')
                
                if pd.notna(timestamp):
                    st.markdown(f"""
                    <div class='activity-card'>
                        <span style='color: {status_color} !important;'>●</span> Task "{task_type}" {task_status} at {timestamp.strftime('%Y-%m-%d %H:%M')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='activity-card'>
                        <span style='color: {status_color} !important;'>●</span> Task "{task_type}" {task_status}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col8:
            st.markdown("#### Key Insights")
            peak_hour = df[df['missed'] == 1]['Hour_of_Day'].mode().iloc[0] if not df[df['missed'] == 1].empty else None
            task_types = df.groupby('Task_Type')['missed'].mean().sort_values(ascending=False) if 'Task_Type' in df.columns else pd.Series()
            high_risk_type = task_types.index[0] if not task_types.empty else "Unknown"
            
            weekend_completion = df[df['Weekend'] == 1]['Task_Status'].eq('Completed').mean() * 100
            weekday_completion = df[df['Weekend'] == 0]['Task_Status'].eq('Completed').mean() * 100
            
            st.markdown(f"""
            <div class='custom-card'>
                <p style='margin: 5px 0;'><span class='status-missed'>●</span> Peak missed tasks occur at {peak_hour}:00</p>
                <p style='margin: 5px 0;'><span class='status-missed'>●</span> {high_risk_type} tasks have the highest risk of being missed</p>
                <p style='margin: 5px 0;'><span class='status-completed'>●</span> Weekend tasks show {weekend_completion:.1f}% completion rate vs {weekday_completion:.1f}% for weekdays</p>
            </div>
            """, unsafe_allow_html=True)

    elif st.session_state.current_page == "Visualization":
        # Import and run the visualization page content
        import pages.visualization
        
    elif st.session_state.current_page == "Prediction":
        # Import and run the prediction page content
        import pages.prediction
        
    elif st.session_state.current_page == "To-Do List":
        # Import and run the to-do list page content
        import pages.todo 