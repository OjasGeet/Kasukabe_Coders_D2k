import joblib
from sklearn.preprocessing import LabelEncoder
import os

# Create models directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

# Create and fit label encoders
task_type_encoder = LabelEncoder()
task_type_encoder.fit(["Maintenance", "Cleaning", "Inspection", "Repair", "Other"])

priority_encoder = LabelEncoder()
priority_encoder.fit(["High", "Medium", "Low"])

time_slot_encoder = LabelEncoder()
time_slot_encoder.fit(["Morning", "Afternoon", "Evening", "Night"])

# Save the encoders
joblib.dump(task_type_encoder, 'models/task_type_encoder.pkl')
joblib.dump(priority_encoder, 'models/priority_encoder.pkl')
joblib.dump(time_slot_encoder, 'models/time_slot_encoder.pkl')

print("Label encoders have been saved to the 'models' directory") 