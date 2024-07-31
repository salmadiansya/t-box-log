import streamlit as st
import pandas as pd
from datetime import datetime

# Constants for file paths
DATASET_FILE = 'dataset/student_data.csv'
LOG_DATA_FILE = 'dataset/log.csv'

# Load student data with caching
@st.cache_data
def load_student_data():
    return pd.read_csv(DATASET_FILE, dtype={'nfc_card_id': str})

# Load log data with error handling
def load_log_data(log_data_file):
    try:
        return pd.read_csv(log_data_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['timestamp', 'student_name', 'student_class', 'nfc_card_id'])

# Define function to add log entry
def add_log_entry(nfc_card_id):
    student_info = student_data[student_data['nfc_card_id'] == nfc_card_id]
    if not student_info.empty:
        student_name = student_info['student_name'].values[0]
        student_class = student_info['student_class'].values[0]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = pd.DataFrame([[timestamp, student_name, student_class, nfc_card_id]], 
                                 columns=['timestamp', 'student_name', 'student_class', 'nfc_card_id'])
        return log_entry
    else:
        return None

# Define function to save log data
def save_log_data(log_data):
    try:
        log_data.to_csv(LOG_DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving log data: {e}")

# Define function to download log data as CSV
def download_log_data(log_data):
    csv = log_data.to_csv(index=False)
    st.download_button(
        label="Download Log Data as CSV",
        data=csv,
        file_name='log_data.csv',
        mime='text/csv'
    )

# Load data
student_data = load_student_data()
log_data = load_log_data(LOG_DATA_FILE)

# Streamlit UI
st.title("MAN10 JAKARTA T-BOX LOG")

# Section to display log data
st.header("Log Notification")
st.write("Use the filter below to view logs for a specific day.")
download_log_data(log_data)

# Date picker for filtering logs by day
selected_date = st.date_input("Select Date", datetime.now())

# Filter log data by selected date
if not log_data.empty:
    log_data['timestamp'] = pd.to_datetime(log_data['timestamp'])
    filtered_log_data = log_data[log_data['timestamp'].dt.date == selected_date]
else:
    filtered_log_data = pd.DataFrame(columns=['timestamp', 'student_name', 'student_class', 'nfc_card_id'])

# Display filtered log data
st.dataframe(filtered_log_data)

# Section to simulate NFC card reading
st.header("Add Log Entry")
nfc_card_id = st.text_input("Enter NFC Card ID")
if st.button("Add Log Entry"):
    log_entry = add_log_entry(nfc_card_id)
    if log_entry is not None:
        log_data = pd.concat([log_data, log_entry], ignore_index=True)
        save_log_data(log_data)
        st.success(f"Log entry added for NFC Card ID: {nfc_card_id}")
    else:
        st.error(f"No student found with NFC Card ID: {nfc_card_id}")

# Section to search logs by student name
st.header("Search by Student Name")
student_name_search = st.text_input("Enter Student Name to Search")
if student_name_search:
    filtered_log_data_by_name = filtered_log_data[filtered_log_data['student_name'].str.contains(student_name_search, case=False, na=False)]
    st.dataframe(filtered_log_data_by_name)
else:
    st.write("Enter the student's name to search for their T-BOX log.")

# Display student data with NFC card ID 0
st.header("Student Data")
st.dataframe(student_data)

# Endpoint for receiving data from ESP32
query_params = st.experimental_get_query_params()
if 'nfc_card_id' in query_params:
    nfc_card_id = query_params['nfc_card_id'][0]
    log_entry = add_log_entry(nfc_card_id)
    if log_entry is not None:
        log_data = pd.concat([log_data, log_entry], ignore_index=True)
        save_log_data(log_data)
        st.write("Log entry added")
    else:
        st.write("No student found with NFC Card ID: ", nfc_card_id)

# Save the current log data on application exit
save_log_data(log_data)
