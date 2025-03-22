import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate dates for the last 3 months
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
dates = pd.date_range(start=start_date, end=end_date, freq='H')

# Generate synthetic data
n_records = len(dates)
data = {
    'Timestamp': dates,
    'Task_Name': [f'Task_{i}' for i in range(n_records)],
    'Task_Type': np.random.choice(['Maintenance', 'Repair', 'Inspection', 'Cleaning', 'Safety Check'], n_records),
    'Task_Status': np.random.choice(['Completed', 'In Progress', 'Missed', 'Scheduled'], n_records, p=[0.6, 0.2, 0.1, 0.1]),
    'Workload_Estimate': np.random.uniform(1, 8, n_records),
    'Task_Frequency': np.random.randint(1, 10, n_records),
    'Priority': np.random.choice(['High', 'Medium', 'Low'], n_records),
    'Assignee': np.random.choice(['John', 'Alice', 'Bob', 'Carol', 'David'], n_records)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('synthetic_facility_tasks_extended.csv', index=False)
print("Synthetic data has been generated and saved to 'synthetic_facility_tasks_extended.csv'") 