import streamlit as st
import pandas as pd
from datetime import datetime

# Konstanta untuk file dataset
DATASET_FILE = 'dataset/student_data.csv'
LOG_DATA_FILE = 'dataset/log.csv'

# Fungsi untuk memuat data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=['timestamp', 'student_name', 'student_class', 'nfc_card_id'])

# Fungsi untuk menambah log entry
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

# Fungsi untuk menyimpan log data
def save_log_data(log_data):
    try:
        log_data.to_csv(LOG_DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving log data: {e}")

# Memuat data
student_data = load_data(DATASET_FILE)
log_data = load_data(LOG_DATA_FILE)

# Streamlit UI
st.title("MAN10 JAKARTA T-BOX LOG")

# Section untuk menampilkan log data
st.header("Log Notification")
if st.button("Refresh"):
    log_data = load_data(LOG_DATA_FILE)
st.dataframe(log_data)

# Section untuk menambah log entry
st.header("Add Log Entry")
nfc_card_id = st.text_input("Enter NFC Card ID")
if st.button("Add Log Entry"):
    log_entry = add_log_entry(nfc_card_id)
    if log_entry is not None:
        log_data = pd.concat([log_data, log_entry], ignore_index=True)
        save_log_data(log_data)
        st.info(f"Log entry added for NFC Card ID: {nfc_card_id}")
    else:
        st.error(f"No student found with NFC Card ID: {nfc_card_id}")

# Section untuk mencari log oleh nama siswa
st.header("Search by Student Name")
student_name_search = st.text_input("Enter Student Name to Search")
if student_name_search:
    filtered_log_data = log_data[log_data['student_name'].str.contains(student_name_search, case=False, na=False)]
    st.dataframe(filtered_log_data)
else:
    st.write("Enter the student's name to search for their T-BOX log.")

# Section untuk menampilkan data siswa
st.header("Student Data")
st.dataframe(student_data)

# Endpoint untuk menerima data dari ESP32
query_params = st.experimental_get_query_params()
if 'nfc_card_id' in query_params:
    nfc_card_id = query_params['nfc_card_id'][0]
    log_entry = add_log_entry(nfc_card_id)
    if log_entry is not None:
        log_data = pd.concat([log_data, log_entry], ignore_index=True)
        save_log_data(log_data)
        st.info(f"Log entry added for NFC Card ID: {nfc_card_id}")
    else:
        st.error(f"No student found with NFC Card ID: {nfc_card_id}")

# Save the current log data on application exit
save_log_data(log_data)
