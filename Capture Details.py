import cv2
import pickle
import numpy as np
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from sklearn.neighbors import KNeighborsClassifier

# Initialize video capture
video = cv2.VideoCapture(0)

# Use a more efficient face detector (HOG, or DNN)
facedetect = cv2.CascadeClassifier('D:/Project/data/haarcascade_frontalface_default.xml')

# Collect face data
faces_data = []
i = 0

# Tkinter window for input
root = tk.Tk()
root.withdraw()  # Hide the root window

# Function to get numeric input for Roll No
def get_numeric_input(prompt):
    while True:
        input_value = simpledialog.askstring("Input", prompt)
        if input_value.isdigit():
            return input_value
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Get user details (name, roll number, enrollment number) using Tkinter
name = simpledialog.askstring("Input", "Enter Your Name:")
roll_no = get_numeric_input("Enter Your Roll Number:")

# Optionally get the Enrollment Number (not restricted to numeric)
enrollment_no = simpledialog.askstring("Input", "Enter Your Enrollment Number (Optional):")

# Start face detection
while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        continue

    # Convert the frame to grayscale (for better processing speed and performance)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = facedetect.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Process each face detected
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(crop_img, (50, 50))  # Resize for consistency

        # Append the face to the faces_data list if conditions are met
        if len(faces_data) < 100 and i % 10 == 0:  # Save every 10th frame
            faces_data.append(resized_img)
        
        i += 1

        # Draw the rectangle around the face
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)

    # Display the frame
    cv2.imshow("Frame", frame)

    # Stop if 'q' is pressed or we have enough faces
    k = cv2.waitKey(1)
    if k == ord('q') or len(faces_data) == 100:
        break

# Release video capture
video.release()
cv2.destroyAllWindows()

# Convert faces data to numpy array and reshape for saving
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(faces_data.shape[0], -1)  # Flatten each face image

# Define file paths
faces_data_file = 'D:/Project/data/faces_data.pkl'
names_file = 'D:/Project/data/names.pkl'
rollnos_file = 'D:/Project/data/rollnos.pkl'
enrollmentnos_file = 'D:/Project/data/enrollmentnos.pkl'

# Save face data and names
if not os.path.exists(names_file):
    # If no names file, create one with the user's name
    names = [name] * 100
    rollnos = [roll_no] * 100  # Store Roll No.
    enrollmentnos = [enrollment_no] * 100  # Store Enrollment No. (can be empty string)
    
    with open(names_file, 'wb') as f:
        pickle.dump(names, f)
    with open(rollnos_file, 'wb') as f:
        pickle.dump(rollnos, f)
    with open(enrollmentnos_file, 'wb') as f:
        pickle.dump(enrollmentnos, f)

else:
    # Load existing names, roll numbers, and enrollment numbers, then append the new user data
    with open(names_file, 'rb') as f:
        names = pickle.load(f)
    with open(rollnos_file, 'rb') as f:
        rollnos = pickle.load(f)
    with open(enrollmentnos_file, 'rb') as f:
        enrollmentnos = pickle.load(f)
    
    # Append new data
    names.extend([name] * 100)
    rollnos.extend([roll_no] * 100)
    enrollmentnos.extend([enrollment_no] * 100)  # Allow empty or non-numeric enrollment number
    
    # Save the updated lists
    with open(names_file, 'wb') as f:
        pickle.dump(names, f)
    with open(rollnos_file, 'wb') as f:
        pickle.dump(rollnos, f)
    with open(enrollmentnos_file, 'wb') as f:
        pickle.dump(enrollmentnos, f)

# Handle faces_data saving
if not os.path.exists(faces_data_file):
    # If no faces data file, create one
    with open(faces_data_file, 'wb') as f:
        pickle.dump(faces_data, f)
else:
    # Load existing faces data and append the new faces data
    with open(faces_data_file, 'rb') as f:
        try:
            existing_faces = pickle.load(f)
        except EOFError:
            existing_faces = np.array([])  # If the file is empty, initialize it as an empty array
    
    existing_faces = np.append(existing_faces, faces_data, axis=0)

    # Save the combined faces data back
    with open(faces_data_file, 'wb') as f:
        pickle.dump(existing_faces, f)

# Train KNN model with the collected face data
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(existing_faces, names)

# Function to mark attendance
def mark_attendance(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        
        # Predict the name using KNN
        prediction = knn.predict(resized_img)
        name = prediction[0]
        
        # Display name and mark attendance on frame
        cv2.putText(frame, f"Name: {name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the frame with attendance information
        cv2.imshow("Attendance Frame", frame)

# Run face recognition in real-time and mark attendance
video = cv2.VideoCapture(0)
while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        continue

    mark_attendance(frame)

    key = cv2.waitKey(1)
    if key == ord('q'):  # Exit on 'q' key press
        break

video.release()
cv2.destroyAllWindows()

print("Attendance system completed successfully.")
