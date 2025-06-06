import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# Get current date and time
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

# Ensure the directory exists
directory = "D:/Project/Attendance"
if not os.path.exists(directory):
    os.makedirs(directory)

# File path for the CSV
file_path = os.path.join(directory, f"Attendance_{date}.csv")

# Create the CSV file if it does not exist
if not os.path.isfile(file_path):
    # Create a DataFrame with column names and save it as CSV
    df = pd.DataFrame(columns=['Name', 'Roll No.', 'Enrollment No.', 'Time'])
    df.to_csv(file_path, index=False)

# Display user input form
st.title("Face Recognition Attendance")
name = st.text_input("Enter Your Name:")
roll_no = st.text_input("Enter Your Roll No.:")
enrollment_no = st.text_input("Enter Your Enrollment No.:")

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Display the DataFrame in Streamlit
st.dataframe(df.style.highlight_max(axis=0))

# Auto-refresh the Streamlit app
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")

# FizzBuzz logic
if count == 0:
    st.write("Count is zero")
elif count % 3 == 0 and count % 5 == 0:
    st.write("FizzBuzz")
elif count % 3 == 0:
    st.write("Fizz")
elif count % 5 == 0:
    st.write("Buzz")
else:
    st.write(f"Count: {count}")

# Capture attendance (when the form is filled)
if st.button("Mark Attendance"):
    if name and roll_no and enrollment_no:
        # Prepare the data to write to CSV
        attendance_data = [name, roll_no, enrollment_no, timestamp]
        with open(file_path, "a", newline='') as csvfile:
            writer = pd.DataFrame([attendance_data], columns=['Name', 'Roll No.', 'Enrollment No.', 'Time'])
            writer.to_csv(csvfile, header=False, index=False)

        # Refresh the displayed attendance
        df = pd.read_csv(file_path)
        st.dataframe(df.style.highlight_max(axis=0))
        st.success("Attendance marked successfully!")
    else:
        st.error("Please fill in all the details before marking attendance.")
