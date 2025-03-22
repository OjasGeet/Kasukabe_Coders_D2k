import joblib

# List of feature names
feature_names = [
    'Facility_ID',
    'Task_Type',
    'Task_Status',
    'Priority',
    'Time_Slot',
    'Scheduled_Year',
    'Scheduled_Month',
    'Scheduled_Day',
    'Scheduled_Weekday',
    'Actual_Start_Hour',
    'Actual_Completion_Hour',
    'Start_Duration',
    'Actual_Duration'
]

# Create models directory if it doesn't exist
import os
if not os.path.exists('models'):
    os.makedirs('models')

# Save feature names to pickle file
joblib.dump(feature_names, 'models/feature_names.pkl')
print("Feature names have been saved to 'models/feature_names.pkl'") 