import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder

# Configure page layout
st.set_page_config(page_title="Task Prediction", page_icon="🔮", layout="wide")

# Add custom CSS to fix the deployment bar and padding
st.markdown("""
    <style>
    /* Fix deployment bar */
    [data-testid="stToolbar"] {
        visibility: hidden;
    }
    
    /* Adjust main content padding */
    .main .block-container {
        padding-top: 2rem !important;
    }
    
    /* Hide decoration */
    [data-testid="stDecoration"] {
        display: none;
    }
    
    /* Adjust header */
    [data-testid="stHeader"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Task Completion Prediction")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Load the trained model
@st.cache_resource
def load_model():
    try:
        # Use os.path.join for proper path handling
        model_path = os.path.join('models', 'xgb_model.pkl')
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error("Model file not found. Please ensure 'xgb_model.pkl' is in the 'models' directory.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

# Load feature names and label encoders
@st.cache_data
def load_feature_names():
    try:
        # Use os.path.join for proper path handling
        feature_names_path = os.path.join('models', 'feature_names.pkl')
        feature_names = joblib.load(feature_names_path)
        return feature_names
    except FileNotFoundError:
        st.error("Feature names file not found. Please ensure 'feature_names.pkl' is in the 'models' directory.")
        return None
    except Exception as e:
        st.error(f"Error loading feature names: {str(e)}")
        return None

# Create input form
def create_input_form():
    st.subheader("Task Details")
    
    # Create two columns for the form
    col1, col2 = st.columns(2)
    
    with col1:
        # Basic task information
        facility_id = st.selectbox("Facility ID", options=[1, 2, 3, 4, 5])
        task_type = st.selectbox("Task Type", options=["Maintenance", "Cleaning", "Inspection", "Repair", "Other"])
        priority = st.selectbox("Priority", options=["High", "Medium", "Low"])
        time_slot = st.selectbox("Time Slot", options=["Morning", "Afternoon", "Evening", "Night"])
        task_frequency = st.number_input("Task Frequency (times per week)", min_value=1, max_value=7, value=1)
        workload_estimate = st.number_input("Workload Estimate (hours)", min_value=0.5, max_value=8.0, value=1.0, step=0.5)
        
        # Scheduled time
        scheduled_date = st.date_input("Scheduled Date")
        scheduled_time = st.time_input("Scheduled Time")
        
    with col2:
        # Actual time information
        actual_start_time = st.time_input("Actual Start Time")
        actual_completion_time = st.time_input("Actual Completion Time")
        
        # Additional features
        delay_duration = st.number_input("Delay Duration (minutes)", min_value=0, max_value=1440, value=0)
        previous_task_delay = st.number_input("Previous Task Delay (minutes)", min_value=0, max_value=1440, value=0)
        rolling_avg_delay = st.number_input("Rolling Average Delay (minutes)", min_value=0, max_value=1440, value=0)
        
        # Calculate durations
        if scheduled_time and actual_start_time:
            start_duration = (datetime.combine(scheduled_date, actual_start_time) - 
                            datetime.combine(scheduled_date, scheduled_time)).total_seconds() / 60
        else:
            start_duration = 0
            
        if actual_start_time and actual_completion_time:
            actual_duration = (datetime.combine(scheduled_date, actual_completion_time) - 
                             datetime.combine(scheduled_date, actual_start_time)).total_seconds() / 60
        else:
            actual_duration = 0
    
    # Create feature dictionary
    input_data = {
        'Facility_ID': facility_id,
        'Task_Type': task_type,
        'Priority': priority,
        'Delay_Duration': delay_duration,
        'Actual_Duration': actual_duration,
        'Workload_Estimate': workload_estimate,
        'Day_of_Week': scheduled_date.weekday(),
        'Time_Slot': time_slot,
        'Task_Frequency': task_frequency,
        'Hour_of_Day': scheduled_time.hour if scheduled_time else 0,
        'Week_of_Year': scheduled_date.isocalendar()[1],
        'Day_of_Month': scheduled_date.day,
        'Weekend': 1 if scheduled_date.weekday() >= 5 else 0,
        'Previous_Task_Delay': previous_task_delay,
        'Rolling_Avg_Delay': rolling_avg_delay,
        'Scheduled_Year': scheduled_date.year,
        'Scheduled_Month': scheduled_date.month,
        'Scheduled_Day': scheduled_date.day,
        'Scheduled_Weekday': scheduled_date.weekday(),
        'Actual_Start_Hour': actual_start_time.hour if actual_start_time else 0,
        'Actual_Completion_Hour': actual_completion_time.hour if actual_completion_time else 0,
        'Start_Duration': start_duration
    }
    
    return input_data

# Convert categorical variables to numerical
def preprocess_input(input_data):
    # Create a copy of the input data
    df = pd.DataFrame([input_data])
    
    # Load label encoders
    try:
        task_type_encoder = joblib.load(os.path.join('models', 'task_type_encoder.pkl'))
        priority_encoder = joblib.load(os.path.join('models', 'priority_encoder.pkl'))
        time_slot_encoder = joblib.load(os.path.join('models', 'time_slot_encoder.pkl'))
        
        # Transform categorical variables
        df['Task_Type'] = task_type_encoder.transform(df['Task_Type'])
        df['Priority'] = priority_encoder.transform(df['Priority'])
        df['Time_Slot'] = time_slot_encoder.transform(df['Time_Slot'])
        
        return df
    except Exception as e:
        st.error(f"Error preprocessing input data: {str(e)}")
        return None

# Display prediction results
def display_prediction_results(prediction, probability):
    st.subheader("Prediction Results")
    
    # Create two columns for results
    col1, col2 = st.columns(2)
    
    with col1:
        # Display prediction
        prediction_text = "Task is likely to be MISSED" if prediction == 1 else "Task is likely to be COMPLETED"
        prediction_color = "red" if prediction == 1 else "green"
        st.markdown(f"### {prediction_text}", unsafe_allow_html=True)
        
        # Display probability gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability * 100,
            title={'text': "Prediction Confidence"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 60], 'color': "gray"},
                    {'range': [60, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': prediction_color, 'width': 4},
                    'thickness': 0.75,
                    'value': probability * 100
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display probability details
        st.markdown("### Probability Details")
        st.markdown(f"- Missed: {probability:.1%}")
        st.markdown(f"- Completed: {(1-probability):.1%}")

# Display model explanation
def display_model_explanation(model, input_data):
    st.subheader("Model Explanation")
    
    # Get feature importance
    try:
        feature_importance = model.feature_importances_
        
        # Get feature names directly from the model
        feature_names = [
            'Facility_ID', 'Task_Type', 'Priority', 'Delay_Duration', 'Actual_Duration',
            'Workload_Estimate', 'Day_of_Week', 'Time_Slot', 'Task_Frequency', 'Hour_of_Day',
            'Week_of_Year', 'Day_of_Month', 'Weekend', 'Previous_Task_Delay', 'Rolling_Avg_Delay',
            'Scheduled_Year', 'Scheduled_Month', 'Scheduled_Day', 'Scheduled_Weekday',
            'Actual_Start_Hour', 'Actual_Completion_Hour', 'Start_Duration'
        ]
        
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': feature_importance
        }).sort_values('Importance', ascending=True)
        
        fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h',
                    title="Feature Importance",
                    labels={'Importance': 'Importance Score', 'Feature': 'Feature Name'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Display top 5 most important features
        st.subheader("Top 5 Most Important Features")
        top_features = importance_df.tail(5)
        for _, row in top_features.iterrows():
            st.markdown(f"- **{row['Feature']}**: {row['Importance']:.4f}")
            
    except Exception as e:
        st.warning(f"Could not display feature importance: {str(e)}")
        st.error("Please ensure the model has feature importance information available.")

# Display recommendations
def display_recommendations(prediction, probability, input_data):
    st.subheader("Recommendations")
    
    if prediction == 1:  # Task likely to be missed
        st.warning("Based on the prediction, this task has a high risk of being missed. Here are some recommendations:")
        
        recommendations = []
        
        # Time-based recommendations
        if input_data['Start_Duration'] > 60:  # More than 1 hour delay
            recommendations.append("Review scheduling process to reduce start time delays")
        
        # Duration-based recommendations
        if input_data['Actual_Duration'] > 240:  # More than 4 hours
            recommendations.append("Consider breaking down the task into smaller subtasks")
        
        # Priority-based recommendations
        if input_data['Priority'] == "High":
            recommendations.append("Allocate additional resources or personnel")
        
        # Display recommendations
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.success("The task is predicted to be completed successfully. Continue with the current plan.")

def main():
    # Load model and feature names
    model = load_model()
    if model is None:
        return
    
    # Create input form
    input_data = create_input_form()
    
    # Create prediction button
    if st.button("Predict Task Completion"):
        # Preprocess input data
        input_df = preprocess_input(input_data)
        if input_df is None:
            return
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        # Display results
        display_prediction_results(prediction, probability)
        display_model_explanation(model, input_data)
        display_recommendations(prediction, probability, input_data)

if __name__ == "__main__":
    main() 