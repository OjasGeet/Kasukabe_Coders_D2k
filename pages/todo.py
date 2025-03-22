import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configure page layout
st.set_page_config(page_title="Task To-Do List", page_icon="✅", layout="wide")
st.title("✅ Facility Task To-Do List")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("facility_tasks (2).csv", encoding="ISO-8859-1")
        df.columns = df.columns.str.strip()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['date'] = df['Timestamp'].dt.date
        df['Due_Date'] = df['Timestamp'] + pd.to_timedelta(np.random.randint(1, 48), unit='h')
        df['Assignee'] = np.random.choice(['John D.', 'Sarah L.', 'Michael T.', 'Emily R.', 'David K.'], size=len(df))
        df['Priority'] = np.random.choice(['High', 'Medium', 'Low'], size=len(df))
        df['Delay'] = np.where(df['Task_Status'] == 'Missed', 
                              np.random.randint(1, 5), 0)
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'facility_tasks (2).csv' is in the correct location.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()

if df is not None:
    # 1. Header Section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("Facility Task Manager")
        
    with col2:
        selected_date = st.date_input("Select Date", value=pd.to_datetime('today').date())
        
    with col3:
        search_query = st.text_input("Search Tasks", placeholder="Search by task name, assignee...")
    
    # Filters
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        status_filter = st.multiselect("Status", 
                                      options=df['Task_Status'].unique().tolist(),
                                      default=df['Task_Status'].unique().tolist())
    
    with col5:
        priority_filter = st.multiselect("Priority", 
                                        options=['High', 'Medium', 'Low'],
                                        default=['High', 'Medium', 'Low'])
    
    with col6:
        assignee_filter = st.multiselect("Assignee", 
                                         options=df['Assignee'].unique().tolist(),
                                         default=df['Assignee'].unique().tolist())
    
    with col7:
        sort_by = st.selectbox("Sort By", 
                              options=["Due Date", "Priority", "Status"],
                              index=0)
    
    # Filter data based on user selections
    filtered_df = df.copy()
    
    # Apply date filter
    filtered_df = filtered_df[filtered_df['date'] == pd.to_datetime(selected_date).date()]
    
    # Apply search filter
    if search_query:
        filtered_df = filtered_df[
            filtered_df['Task_Name'].str.contains(search_query, case=False) |
            filtered_df['Assignee'].str.contains(search_query, case=False) |
            filtered_df['Task_Type'].str.contains(search_query, case=False)
        ]
    
    # Apply status filter
    if status_filter:
        filtered_df = filtered_df[filtered_df['Task_Status'].isin(status_filter)]
    
    # Apply priority filter
    if priority_filter:
        filtered_df = filtered_df[filtered_df['Priority'].isin(priority_filter)]
    
    # Apply assignee filter
    if assignee_filter:
        filtered_df = filtered_df[filtered_df['Assignee'].isin(assignee_filter)]
    
    # Sort data
    if sort_by == "Due Date":
        filtered_df = filtered_df.sort_values('Due_Date')
    elif sort_by == "Priority":
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        filtered_df['Priority_Order'] = filtered_df['Priority'].map(priority_order)
        filtered_df = filtered_df.sort_values('Priority_Order')
    elif sort_by == "Status":
        filtered_df = filtered_df.sort_values('Task_Status')
    
    # 2. Summary Overview Section
    st.markdown("---")
    st.subheader("📊 Summary Overview")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    total_tasks = len(filtered_df)
    completed_tasks = len(filtered_df[filtered_df['Task_Status'] == 'Completed'])
    pending_tasks = len(filtered_df[filtered_df['Task_Status'] == 'In Progress'])
    delayed_tasks = len(filtered_df[filtered_df['Task_Status'] == 'Missed'])
    high_priority_tasks = len(filtered_df[filtered_df['Priority'] == 'High'])
    
    with metric_col1:
        st.metric("Total Tasks", total_tasks)
    
    with metric_col2:
        st.metric("Completed", completed_tasks, f"{int(completed_tasks/total_tasks*100)}%" if total_tasks > 0 else "0%")
    
    with metric_col3:
        st.metric("Pending", pending_tasks, f"{int(pending_tasks/total_tasks*100)}%" if total_tasks > 0 else "0%")
    
    with metric_col4:
        st.metric("Delayed", delayed_tasks, f"{int(delayed_tasks/total_tasks*100)}%" if total_tasks > 0 else "0%")
    
    with metric_col5:
        st.metric("High Priority", high_priority_tasks, f"{int(high_priority_tasks/total_tasks*100)}%" if total_tasks > 0 else "0%")
    
    # 3. To-Do List Section
    st.markdown("---")
    st.subheader("📋 Task List")
    
    def get_status_color(status):
        colors = {
            'Completed': 'green',
            'In Progress': 'blue',
            'Missed': 'red',
            'Scheduled': 'orange'
        }
        return colors.get(status, 'gray')
    
    def get_priority_icon(priority):
        icons = {
            'High': '🔥',
            'Medium': '⚠️',
            'Low': '📌'
        }
        return icons.get(priority, '')
        
    # Custom CSS for table
    st.markdown("""
    <style>
    .task-table {
        width: 100%;
        border-collapse: collapse;
    }
    .task-table th {
        background-color: #f0f2f6;
        padding: 10px;
        text-align: left;
        font-weight: bold;
    }
    .task-table td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 0.8em;
    }
    .task-row:hover {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if len(filtered_df) > 0:
        # Convert to a table with custom formatting
        table_html = """
        <table class="task-table">
            <tr>
                <th>Task Name</th>
                <th>Status</th>
                <th>Assignee</th>
                <th>Priority</th>
                <th>Due Date</th>
                <th>Delay (Days)</th>
            </tr>
        """
        
        for _, row in filtered_df.iterrows():
            status_color = get_status_color(row['Task_Status'])
            priority_icon = get_priority_icon(row['Priority'])
            due_date = pd.to_datetime(row['Due_Date']).strftime('%Y-%m-%d %H:%M')
            delay = row['Delay']
            delay_display = f"{delay} days" if delay > 0 else "-"
            
            table_html += f"""
            <tr class="task-row" onclick="this.classList.toggle('selected')">
                <td>{row['Task_Name']}</td>
                <td><span class="status-badge" style="background-color: {status_color};">{row['Task_Status']}</span></td>
                <td>{row['Assignee']}</td>
                <td>{priority_icon} {row['Priority']}</td>
                <td>{due_date}</td>
                <td>{delay_display}</td>
            </tr>
            """
        
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Task Actions
        col_actions1, col_actions2, col_actions3 = st.columns(3)
        
        with col_actions1:
            if st.button("Complete Selected Tasks"):
                st.success("Selected tasks marked as completed!")
        
        with col_actions2:
            if st.button("Reassign Selected Tasks"):
                st.info("Task reassignment modal would open here")
        
        with col_actions3:
            if st.button("Edit Selected Tasks"):
                st.info("Task edit modal would open here")
    else:
        st.info("No tasks found for the selected filters")
    
    # 4. Task Progress Management
    st.markdown("---")
    st.subheader("⏳ Task Progress")
    
    # Task status counts
    status_counts = df['Task_Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig = px.pie(status_counts, values='Count', names='Status', 
                 title='Task Status Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Task Details Modal (simulated)
    st.markdown("---")
    st.subheader("📅 Task Details")
    
    task_selection = st.selectbox("Select a task to view details", 
                                 options=filtered_df['Task_Name'].tolist() if not filtered_df.empty else ["No tasks available"])
    
    if task_selection != "No tasks available":
        selected_task = filtered_df[filtered_df['Task_Name'] == task_selection].iloc[0]
        
        col_details1, col_details2 = st.columns(2)
        
        with col_details1:
            st.markdown(f"**Task Name:** {selected_task['Task_Name']}")
            st.markdown(f"**Task Type:** {selected_task['Task_Type']}")
            st.markdown(f"**Status:** {selected_task['Task_Status']}")
            st.markdown(f"**Priority:** {get_priority_icon(selected_task['Priority'])} {selected_task['Priority']}")
            
        with col_details2:
            st.markdown(f"**Assignee:** {selected_task['Assignee']}")
            st.markdown(f"**Due Date:** {pd.to_datetime(selected_task['Due_Date']).strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Delay:** {selected_task['Delay']} days")
            st.markdown(f"**Created At:** {pd.to_datetime(selected_task['Timestamp']).strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("### Task Description")
        st.write("Detailed task description would appear here.")
        
        st.markdown("### Activity Log")
        st.write("Task activity history would appear here.")
        
        # Comments section
        st.markdown("### Comments")
        user_comment = st.text_area("Add a comment")
        if st.button("Post Comment"):
            st.success("Comment added!")
    
    # 6. Today's Updates Section
    st.markdown("---")
    st.subheader("📅 Today's Updates")
    
    # Create a simulated updates dataframe
    updates_data = {
        'Task_Name': filtered_df['Task_Name'].tolist()[:5] if len(filtered_df) >= 5 else filtered_df['Task_Name'].tolist(),
        'Action': ['Status Changed', 'Created', 'Priority Changed', 'Reassigned', 'Completed'],
        'Performed_By': ['John D.', 'Sarah L.', 'Michael T.', 'Emily R.', 'David K.'],
        'Time': [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(5)]
    }
    
    if len(updates_data['Task_Name']) > 0:
        updates_df = pd.DataFrame(updates_data)
        st.dataframe(updates_df, use_container_width=True)
    else:
        st.info("No updates for today")
    
    # 7. Calendar View (simplified)
    st.markdown("---")
    st.subheader("📆 Calendar View")
    
    # Group tasks by date
    date_counts = df.groupby('date').size().reset_index(name='counts')
    
    fig = px.bar(date_counts, x='date', y='counts', 
                 title='Tasks by Date',
                 labels={'date': 'Date', 'counts': 'Number of Tasks'})
    st.plotly_chart(fig, use_container_width=True)
    
    # 8. Filters and Search Section (already implemented at the top)
    
    # 9. Data Export
    st.markdown("---")
    st.subheader("🛠 Additional Features")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if st.button("Export to CSV"):
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="task_export.csv",
                mime="text/csv"
            )
    
    with col_export2:
        if st.button("Generate Task Report"):
            st.info("Task report generation would start here")

else:
    st.error("Failed to load data. Please check that the dataset exists and has the required structure.") 