import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Configure page layout and title
st.set_page_config(page_title="Facility Task Dashboard", page_icon=":bar_chart:", layout="wide")
st.title("Facility Task Analysis Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ------------- Data Loading & Preprocessing -------------
@st.cache_data
def load_data():
    # Load the provided dataset from a local CSV file
    df = pd.read_csv("facility_tasks (2).csv", encoding="ISO-8859-1")
    df.columns = df.columns.str.strip()
    # Convert 'Timestamp' to datetime and create a date column
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['date'] = df['Timestamp'].dt.date
    # Create a binary indicator for missed tasks (assumes Task_Status uses "missed" for missed tasks)
    df['missed'] = (df['Task_Status'].str.lower() == "missed").astype(int)
    # Create Day_of_Month and Hour_of_Day columns for the heatmap
    df['Day_of_Month'] = df['Timestamp'].dt.day
    df['Hour_of_Day'] = df['Timestamp'].dt.hour
    return df

df = load_data()

# ------------- Sidebar Filters -------------
st.sidebar.header("Filter Options")

# Date Range Filter
date_min = df['date'].min()
date_max = df['date'].max()
date_range = st.sidebar.date_input("Select Date Range", [date_min, date_max])
df = df[(df['date'] >= date_range[0]) & (df['date'] <= date_range[1])]

# Multi-select filters for Task Status and Task Type
selected_status = st.sidebar.multiselect("Select Task Status",
                                           options=df["Task_Status"].unique(),
                                           default=df["Task_Status"].unique())
selected_task_type = st.sidebar.multiselect("Select Task Type",
                                              options=df["Task_Type"].unique(),
                                              default=df["Task_Type"].unique())
df = df[df["Task_Status"].isin(selected_status) & df["Task_Type"].isin(selected_task_type)]

st.write(f"### Showing {len(df)} records from {date_range[0]} to {date_range[1]}")

# ------------- Layout the Visualizations -------------

# Dynamic Heatmap (stacked)
st.subheader("📊 Monthly Task Miss Heatmap")

# 🎛 *Filters Above the Heatmap*
selected_days = st.multiselect("Select Days of the Month", sorted(df["Day_of_Month"].unique()), default=sorted(df["Day_of_Month"].unique())[:5])
selected_hours = st.multiselect("Select Hours", sorted(df["Hour_of_Day"].unique()), default=sorted(df["Hour_of_Day"].unique()))
task_types = df["Task_Type"].unique() if "Task_Type" in df.columns else []
selected_task = st.selectbox("Select Task Type", ["All"] + list(task_types.tolist())) if task_types.size > 0 else None
show_values = st.checkbox("Show Heatmap Values", value=True)

# 🎯 *Filter Data Based on User Selection*
filtered_df = df[df["Day_of_Month"].isin(selected_days) & df["Hour_of_Day"].isin(selected_hours)]

# Apply task type filter if applicable
if selected_task and selected_task != "All":
    filtered_df = filtered_df[filtered_df["Task_Type"] == selected_task]

# Pivot the data for heatmap
heatmap_data = filtered_df.pivot_table(
    index="Day_of_Month",
    columns="Hour_of_Day",
    aggfunc="size",
    fill_value=0
)

# 🎨 *Create Heatmap with Optional Values*
fig_heatmap = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale="Blues",
    hoverongaps=False,
    text=heatmap_data.values if show_values else None,
    texttemplate="%{z}" if show_values else None,  # Show values only if checked
    textfont={"size": 12}
))

# 📏 *Increase Heatmap Size*
fig_heatmap.update_layout(
    title="Monthly Task Miss Heatmap",
    xaxis_title="Hour of Day",
    yaxis_title="Day of Month",
    width=1000,
    height=700
)

st.plotly_chart(fig_heatmap, use_container_width=False)  # Display heatmap


# Daily Trend Graph (stacked below heatmap)
st.subheader("Daily Trend of Missed Tasks")
daily_trend = df.groupby("date").agg({"missed": "sum"}).reset_index()
daily_trend.columns = ["date", "missed_count"]
fig_daily = px.line(daily_trend, x="date", y="missed_count",
                    title="Daily Trend of Missed Tasks",
                    labels={"date": "Date", "missed_count": "Number of Missed Tasks"})
fig_daily.update_traces(mode="markers+lines")
st.plotly_chart(fig_daily, use_container_width=True)

# Second Row: Risk Gauge and Weekend vs. Weekday Performance in columns
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
    # Create a Weekend indicator if missing (using Timestamp's day of week)
    if 'Weekend' not in df.columns:
        df['Weekend'] = pd.to_datetime(df['Timestamp']).dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
    weekend_status = df.groupby(["Weekend", "Task_Status"]).size().reset_index(name="count")
    fig4 = px.bar(weekend_status, x="Weekend", y="count", color="Task_Status", barmode="group",
                  title="Task Performance: Weekend vs. Weekday",
                  labels={"Weekend": "Weekend (1 = Yes, 0 = No)", "count": "Number of Tasks", "Task_Status": "Task Status"})
    fig4.update_traces(texttemplate="%{y}", textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)

# Third Row: SHAP Summary Plot (within an expander)
st.subheader("Feature Importance via SHAP")
with st.expander("View SHAP Summary Plot"):

    # Apply a white background to the entire expander
    st.markdown("""
        <style>
        .streamlit-expanderContent {
            background-color: white !important;
            color: black !important;
            border-radius: 10px;
            padding: 1rem;
        }
        .element-container:has(div[data-testid="stExpander"]) {
            background-color: white !important;
            border-radius: 10px;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stExpander"] {
            background-color: white !important;
            border-radius: 10px;
        }
        div[data-testid="stImage"] {
            background-color: white !important;
            padding: 1rem;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Allow user to select features dynamically
    available_features = df.select_dtypes(include=['number']).columns.tolist()
    selected_features = st.multiselect("Select Features for SHAP Analysis", available_features, default=available_features[:3])

    if len(selected_features) >= 2:  # Ensure at least 2 features are selected for meaningful analysis
        X = df[selected_features].fillna(0)
        y = df['missed']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        model.fit(X_train, y_train)

        # Generate SHAP values
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)

        # Create a white figure with full white background
        fig_shap = plt.figure(figsize=(12, 7), facecolor='white')
        
        # Set all elements to have white background
        plt.rcParams.update({
            'figure.facecolor': 'white', 
            'axes.facecolor': 'white',
            'savefig.facecolor': 'white',
            'text.color': 'black',
            'axes.labelcolor': 'black',
            'xtick.color': 'black',
            'ytick.color': 'black',
            'figure.edgecolor': 'white',
            'savefig.edgecolor': 'white'
        })
        
        # Set a white background for the matplotlib figure
        ax = plt.gca()
        ax.set_facecolor('white')
        fig_shap.patch.set_facecolor('white')
        
        # Create SHAP summary plot with explicit background color
        shap.summary_plot(
            shap_values, 
            X_test, 
            feature_names=selected_features, 
            show=False, 
            plot_size=(12, 7),
            color_bar_label='Feature value',
            plot_type='dot'
        )
        
        # Add padding and ensure all text is visible
        plt.tight_layout(pad=2.0)
        
        # Render the plot with a white background
        st.pyplot(fig_shap)

    else:
        st.warning("Please select at least two numerical features for SHAP analysis.")


# Optional: Download filtered data button
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Filtered Data", data=csv, file_name="Filtered_Data.csv", mime="text/csv") 