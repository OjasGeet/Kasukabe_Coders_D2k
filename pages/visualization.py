import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Try importing optional dependencies
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    st.warning("Matplotlib and Seaborn are not installed. Some visualizations may be limited.")

try:
    import shap
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    st.warning("Machine learning libraries (XGBoost, SHAP) are not installed. SHAP analysis will not be available.")

# Configure page layout and title
st.set_page_config(page_title="Task Visualization", page_icon="📈", layout="wide")
st.title("Task Analysis Visualization")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ------------- Data Loading & Preprocessing -------------
@st.cache_data
def load_data():
    try:
        # Load the provided dataset from a local CSV file
        df = pd.read_csv("facility_tasks (2).csv", encoding="ISO-8859-1")
        df.columns = df.columns.str.strip()
        # Convert 'Timestamp' to datetime and create a date column
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['date'] = df['Timestamp'].dt.date
        # Create a binary indicator for missed tasks
        df['missed'] = (df['Task_Status'].str.lower() == "missed").astype(int)
        # Create Day_of_Month and Hour_of_Day columns for the heatmap
        df['Day_of_Month'] = df['Timestamp'].dt.day
        df['Hour_of_Day'] = df['Timestamp'].dt.hour
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'facility_tasks (2).csv' is in the correct location.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()

if df is not None:
    # ------------- Sidebar Filters -------------
    st.sidebar.header("Filter Options")

    # Date Range Filter
    date_min = df['date'].min()
    date_max = df['date'].max()
    date_range = st.sidebar.date_input("Select Date Range", [date_min, date_max])
    df = df[(df['date'] >= date_range[0]) & (df['date'] <= date_range[1])]

    # Multi-select filters for Task Status and Task Type
    selected_status = st.sidebar.multiselect(
        "Select Task Status",
        options=df["Task_Status"].unique(),
        default=df["Task_Status"].unique()
    )
    selected_task_type = st.sidebar.multiselect(
        "Select Task Type",
        options=df["Task_Type"].unique(),
        default=df["Task_Type"].unique()
    )
    df = df[df["Task_Status"].isin(selected_status) & df["Task_Type"].isin(selected_task_type)]

    # Display record count and date range
    st.write(f"### Showing {len(df)} records from {date_range[0]} to {date_range[1]}")
    
    # Help text for filters
    with st.expander("How to use the filters"):
        st.markdown("""
        - **Date Range:** Use the date picker to choose the start and end dates. The dashboard will update to display records only within this range.
        - **Task Status & Task Type:** Select one or multiple options from the multiselect boxes. Only records matching your selections are used in the visualizations.
        """)

    # ------------- Layout the Visualizations -------------

    # First Row: Dynamic Heatmap and Daily Trend
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Task Miss Heatmap")
        # Pivot the data to create a matrix for missed tasks
        heatmap_data = df[df['missed'] == 1].pivot_table(
            index='Day_of_Month', 
            columns='Hour_of_Day', 
            aggfunc='size', 
            fill_value=0
        )
        # Create an interactive heatmap using Plotly
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Blues',
            hoverongaps=False
        ))
        fig_heatmap.update_layout(
            title="Monthly Task Miss Heatmap",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Month"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with col2:
        st.subheader("Daily Trend of Missed Tasks")
        daily_trend = df.groupby("date").agg({"missed": "sum"}).reset_index()
        daily_trend.columns = ["date", "missed_count"]
        fig_daily = px.line(daily_trend, x="date", y="missed_count",
                            title="Daily Trend of Missed Tasks",
                            labels={"date": "Date", "missed_count": "Number of Missed Tasks"})
        fig_daily.update_traces(mode="markers+lines")
        st.plotly_chart(fig_daily, use_container_width=True)

    # Second Row: Risk Gauge and Weekend vs. Weekday Performance
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Overall Task Miss Risk Gauge")
        total_tasks = len(df)
        total_missed = df["missed"].sum()
        risk_score = (total_missed / total_tasks) * 100 if total_tasks > 0 else 0
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Overall Task Miss Risk (%)"},
            gauge={'axis': {'range': [0, 100]},
                   'steps': [
                       {'range': [0, 30], 'color': "green"},
                       {'range': [30, 60], 'color': "yellow"},
                       {'range': [60, 100], 'color': "red"}],
                  }
        ))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Task Performance: Weekend vs. Weekday")
        # Create a Weekend indicator if missing
        if 'Weekend' not in df.columns:
            df['Weekend'] = pd.to_datetime(df['Timestamp']).dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
        weekend_status = df.groupby(["Weekend", "Task_Status"]).size().reset_index(name="count")
        fig4 = px.bar(weekend_status, x="Weekend", y="count", color="Task_Status", barmode="group",
                      title="Task Performance: Weekend vs. Weekday",
                      labels={"Weekend": "Weekend (1 = Yes, 0 = No)", "count": "Number of Tasks", "Task_Status": "Task Status"})
        fig4.update_traces(texttemplate="%{y}", textposition="outside")
        st.plotly_chart(fig4, use_container_width=True)

    # Third Row: SHAP Summary Plot (within an expander)
    if ML_AVAILABLE:
        st.subheader("Feature Importance via SHAP")
        with st.expander("View SHAP Summary Plot"):
            # Ensure required features exist before performing SHAP analysis
            features = ['Workload_Estimate', 'Hour_of_Day', 'Task_Frequency']
            if all(f in df.columns for f in features):
                X = df[features].fillna(0)
                y = df['missed']
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
                model.fit(X_train, y_train)
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test)
                # Create a matplotlib figure for the SHAP summary plot
                fig_shap = plt.figure(figsize=(10, 6))
                shap.summary_plot(shap_values, X_test, feature_names=features, show=False)
                st.pyplot(fig_shap)
            else:
                st.warning("Required features for SHAP analysis are missing. Please ensure the following features exist in your dataset: Workload_Estimate, Hour_of_Day, Task_Frequency")
    else:
        st.info("SHAP analysis is not available. Please install required packages (XGBoost, SHAP) to enable this feature.")

    # Data Export Section
    st.markdown("---")
    st.subheader("Export Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered Data",
        data=csv,
        file_name="Filtered_Data.csv",
        mime="text/csv"
    ) 