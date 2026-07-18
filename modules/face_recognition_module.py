"""
Face Recognition Module for Smart Classroom AI
Handles face detection, recognition, and student identification
"""

import cv2
import numpy as np
import pickle
import os
from datetime import datetime
import json

# Try to import face_recognition library (optional dependency)
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ face_recognition library not installed. Face recognition features disabled.")
    print("   To enable: pip install face-recognition")

# Paths
FACE_DATABASE_PATH = "face_database"
ENCODINGS_FILE = "face_encodings.pkl"
STUDENTS_FILE = "students.json"

# Create directories
os.makedirs(FACE_DATABASE_PATH, exist_ok=True)


class FaceRecognitionSystem:
    def __init__(self):
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError("face_recognition library not available")
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.students_db = {}
        self.load_face_database()
    
    def load_face_database(self):
        """Load known faces from database"""
        try:
            # Load encodings
            if os.path.exists(ENCODINGS_FILE):
                with open(ENCODINGS_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                    self.known_face_ids = data['ids']
                print(f"✅ Loaded {len(self.known_face_names)} faces from database")
            
            # Load student information
            if os.path.exists(STUDENTS_FILE):
                with open(STUDENTS_FILE, 'r') as f:
                    self.students_db = json.load(f)
                print(f"✅ Loaded {len(self.students_db)} student records")
        except Exception as e:
            print(f"⚠️ Error loading face database: {e}")
    
    def save_face_database(self):
        """Save face encodings to file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names,
                'ids': self.known_face_ids
            }
            with open(ENCODINGS_FILE, 'wb') as f:
                pickle.dump(data, f)
            
            with open(STUDENTS_FILE, 'w') as f:
                json.dump(self.students_db, f, indent=2)
            
            print("✅ Face database saved successfully")
            return True
        except Exception as e:
            print(f"❌ Error saving face database: {e}")
            return False
    
    def enroll_student(self, student_id, student_name, image_path):
        """
        Enroll a new student by extracting face encoding from image
        
        Args:
            student_id: Unique student ID (e.g., "21BCE1234")
            student_name: Student's full name
            image_path: Path to student's photo
        
        Returns:
            bool: Success status
        """
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect face locations
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                print(f"❌ No face detected in {image_path}")
                return False
            
            if len(face_locations) > 1:
                print(f"⚠️ Multiple faces detected, using first face")
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            face_encoding = face_encodings[0]
            
            # Add to database
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(student_name)
            self.known_face_ids.append(student_id)
            
            # Store student info
            self.students_db[student_id] = {
                'name': student_name,
                'enrolled_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image_path': image_path
            }
            
            # Save to disk
            self.save_face_database()
            
            print(f"✅ Enrolled: {student_name} ({student_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error enrolling student: {e}")
            return False
    
    def recognize_faces(self, frame):
        """
        Recognize faces in a frame
        
        Args:
            frame: OpenCV image frame
        
        Returns:
            tuple: (annotated_frame, recognized_students)
        """
        if len(self.known_face_encodings) == 0:
            return frame, []
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_students = []
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding,
                tolerance=0.6  # Lower = stricter matching
            )
            
            name = "Unknown"
            student_id = "Unknown"
            confidence = 0
            
            # Use face with smallest distance
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encoding
            )
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    student_id = self.known_face_ids[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                    
                    recognized_students.append({
                        'id': student_id,
                        'name': name,
                        'confidence': confidence,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
            
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw box around face
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            
            label = f"{name}"
            if confidence > 0:
                label += f" ({confidence*100:.0f}%)"
            
            cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
        
        return frame, recognized_students
    
    def get_student_info(self, student_id):
        """Get student information by ID"""
        return self.students_db.get(student_id, None)
    
    def list_enrolled_students(self):
        """Get list of all enrolled students"""
        return [
            {
                'id': sid,
                'name': info['name'],
                'enrolled_date': info['enrolled_date']
            }
            for sid, info in self.students_db.items()
        ]
    
    def delete_student(self, student_id):
        """Remove a student from the database"""
        try:
            if student_id in self.students_db:
                # Find index
                idx = self.known_face_ids.index(student_id)
                
                # Remove from lists
                del self.known_face_encodings[idx]
                del self.known_face_names[idx]
                del self.known_face_ids[idx]
                del self.students_db[student_id]
                
                # Save
                self.save_face_database()
                print(f"✅ Deleted student: {student_id}")
                return True
            else:
                print(f"⚠️ Student not found: {student_id}")
                return False
        except Exception as e:
            print(f"❌ Error deleting student: {e}")
            return False


# Global instance (only create if face_recognition is available)
if FACE_RECOGNITION_AVAILABLE:
    face_recognition_system = FaceRecognitionSystem()
else:
    face_recognition_system = None
