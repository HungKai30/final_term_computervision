import os
import cv2
import face_recognition
import numpy as np
import mysql.connector
import sys
import csv
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')
# MySQL setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'attendance_system'
}

def fetch_student_faces(class_id, root_path):
    """
    Fetch student face encodings and details from the database.
    """
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    sql = "SELECT student_id, face_image FROM students WHERE class_id = %s AND face_image IS NOT NULL AND face_image != ''"
    cursor.execute(sql, (class_id,))
    students = cursor.fetchall()

    student_faces = []
    for student in students:
        if student['face_image']:
            # Sửa đường dẫn tại đây
            face_image_path = os.path.join(root_path, '..', 'frontend', 'uploads', student['face_image'])
            print(f"Đường dẫn đầy đủ: {face_image_path}")

            if os.path.exists(face_image_path):
                try:
                    face_image = face_recognition.load_image_file(face_image_path)
                    face_encodings = face_recognition.face_encodings(face_image)
                    if face_encodings:
                        face_encoding = face_encodings[0]
                        student_faces.append({'student_id': student['student_id'], 'encoding': face_encoding})
                    else:
                        print(f"No face detected in image: {face_image_path}")
                except Exception as e:
                    print(f"Error loading or processing image: {face_image_path} - {e}")
            else:
                print(f"Image not found: {face_image_path}")

    connection.close()
    return student_faces

def process_video_and_attendance(video_path, class_id, root_path):
    """
    Process the video for attendance and return list of present student IDs.
    """
    print("Bắt đầu process_video_and_attendance") # Debug
    student_faces = fetch_student_faces(class_id, root_path)
    if not student_faces:
        print("Không tìm thấy khuôn mặt sinh viên nào trong cơ sở dữ liệu.")
        return []
    print(f"Student faces found: {student_faces}") # Debug
    known_encodings = [s['encoding'] for s in student_faces]
    student_ids = [s['student_id'] for s in student_faces]

    print(f"Known encodings: {known_encodings}") # Debug
    print(f"Student IDs: {student_ids}") # Debug
    


    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error: Could not open video at {video_path}.")
        return []
    
 

    
 
                