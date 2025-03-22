import streamlit as st
import pandas as pd

# Configure page layout
st.set_page_config(page_title="Task To-Do List", page_icon="✅", layout="wide")
st.title("✅ Facility Task To-Do List")

# Initialize session state for the to-do list if not already initialized
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Function to add a task to the list
def add_task(task, status, priority):
    st.session_state.tasks.append({
        'task': task, 
        'Completed': False, 
        'Delayed': False, 
        'Missed': False,
        'Priority': priority
    })
    st.session_state.tasks[-1][status] = True

# Function to update task status
def update_task(index, status):
    # Reset all statuses before setting the new one
    st.session_state.tasks[index]['Completed'] = False
    st.session_state.tasks[index]['Delayed'] = False
    st.session_state.tasks[index]['Missed'] = False
    # Set the new status
    st.session_state.tasks[index][status] = True
    # Force a rerun to update the display
    st.rerun()

# Input form to add a new task
with st.form(key='add_task_form'):
    col1, col2 = st.columns(2)
    with col1:
        task_input = st.text_input('Enter a new task:')
        priority_input = st.selectbox('Priority:', ['High', 'Medium', 'Low'])
    with col2:
        status_input = st.selectbox('Status:', ['Completed', 'Delayed', 'Missed'])
        submit_button = st.form_submit_button('Add Task')

    if submit_button and task_input:
        add_task(task_input, status_input, priority_input)
        st.success(f'Task "{task_input}" added successfully!')
        st.rerun()

# Display the to-do list as a table
st.subheader('Tasks:')
if st.session_state.tasks:
    # Create a DataFrame to display the tasks in a table format
    tasks_df = pd.DataFrame(st.session_state.tasks)
    
    # Reorder columns for better display
    tasks_df = tasks_df[['task', 'Priority', 'Completed', 'Delayed', 'Missed']]
    
    # Rename columns for better display
    tasks_df.columns = ['Task', 'Priority', 'Completed', 'Delayed', 'Missed']
    
    # Sort by priority (High -> Medium -> Low)
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    tasks_df['Priority_Order'] = tasks_df['Priority'].map(priority_order)
    tasks_df = tasks_df.sort_values('Priority_Order')
    tasks_df = tasks_df.drop('Priority_Order', axis=1)

    # Display the table
    st.dataframe(tasks_df, use_container_width=True)

    # Edit task status
    st.subheader('Update Task Status')
    for index, task in enumerate(st.session_state.tasks):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_status = st.selectbox(
                f"Update status for '{task['task']}'",
                ['Completed', 'Delayed', 'Missed'],
                index=['Completed', 'Delayed', 'Missed'].index('Completed' if task['Completed'] else 'Delayed' if task['Delayed'] else 'Missed'),
                key=f'progress_{index}'
            )
        with col2:
            if st.button(f'Update', key=f'update_{index}'):
                update_task(index, new_status)
                st.success(f"Status for task '{task['task']}' updated to {new_status}.")
else:
    st.write("No tasks available.") 