# Face Recognition Attendance System - Setup Guide

## Overview
The Smart Classroom AI now supports face recognition-based attendance tracking, replacing generic "Student_001" entries with actual student names and IDs.

## Installation

### 1. Install Required Libraries
```bash
# Activate your virtual environment first
yolo311\Scripts\activate.bat

# Install face recognition dependencies
pip install face-recognition dlib numpy
```

**Note**: Installing `dlib` on Windows may require Visual Studio C++ Build Tools. If you encounter issues:
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Or use pre-built wheels: `pip install dlib-19.24.0-cp311-cp311-win_amd64.whl`

### 2. Verify Installation
```bash
python -c "import face_recognition; print('Face recognition installed successfully!')"
```

## How It Works

### Face Recognition Process:
1. **Enrollment**: Upload student photos with ID and name
2. **Face Encoding**: System extracts 128-dimensional face embeddings
3. **Real-Time Recognition**: Camera detects and matches faces
4. **Attendance Tracking**: Recognized students appear with their real names

### Key Features:
- ✅ Real student names instead of generic IDs
- ✅ Confidence scores for each recognition
- ✅ Multiple students recognized simultaneously
- ✅ Persistent face database (survives restarts)
- ✅ Easy enrollment through web interface

## Usage

### Step 1: Enroll Students

1. Navigate to: `http://127.0.0.1:5000/face/enroll`
2. Fill in the form:
   - **Student ID**: e.g., `21BCE1234`
   - **Full Name**: e.g., `John Doe`
   - **Photo**: Upload a clear face photo (front-facing, good lighting)
3. Click "Enroll Student"

**Photo Requirements:**
- Clear, front-facing photo
- Good lighting
- Only one face in the photo
- Recommended: 640x480 or higher resolution
- Formats: JPG, PNG

### Step 2: Enable Face Recognition

In `modules/camera_module.py`, ensure:
```python
use_face_recognition = True  # Set to True for face recognition
```

### Step 3: Start the System

```bash
python app.py
```

### Step 4: View Attendance

- Dashboard shows: `✓ John Doe - 21BCE1234 (95%)`
- Confidence percentage indicates recognition accuracy
- Export attendance with real names to Excel

## Configuration

### Toggle Between Modes

**Face Recognition Mode** (Default):
```python
# modules/camera_module.py
use_face_recognition = True
```

**Person Detection Mode** (Generic counting):
```python
# modules/camera_module.py
use_face_recognition = False
```

### Adjust Recognition Sensitivity

In `modules/face_recognition_module.py`:
```python
# Line 145: Lower = stricter matching
matches = face_recognition.compare_faces(
    self.known_face_encodings, 
    face_encoding,
    tolerance=0.6  # Default: 0.6, Range: 0.4-0.7
)
```

- **0.4**: Very strict (fewer false positives, may miss some matches)
- **0.6**: Balanced (recommended)
- **0.7**: Lenient (more matches, higher false positive rate)

## File Structure

```
smart_room/
├── face_database/          # Stores student photos
│   ├── 21BCE1234.jpg
│   └── 21BCE5678.jpg
├── face_encodings.pkl      # Face embeddings database
├── students.json           # Student information
└── modules/
    └── face_recognition_module.py
```

## API Endpoints

### Enroll Student
```
POST /face/enroll
Form Data:
  - student_id: string
  - student_name: string
  - photo: file
```

### Get Enrolled Students
```
GET /face/students
Response: {
  "success": true,
  "students": [...]
}
```

### Delete Student
```
DELETE /face/delete/<student_id>
```

### Reload Database
```
POST /face/reload
```

## Troubleshooting

### Issue: "No face detected in photo"
**Solution**: 
- Use a clearer photo with better lighting
- Ensure face is front-facing
- Check that only one face is in the photo

### Issue: "dlib installation failed"
**Solution**:
- Install Visual Studio C++ Build Tools
- Or use pre-compiled wheel for Windows

### Issue: Low recognition accuracy
**Solution**:
- Re-enroll with better quality photos
- Adjust tolerance value (increase for more lenient matching)
- Ensure good lighting in classroom

### Issue: Slow performance
**Solution**:
- Frame is resized to 25% for faster processing
- Reduce camera resolution if needed
- Consider using GPU acceleration

## Performance Tips

1. **Optimal Photo Quality**: 
   - 640x480 minimum resolution
   - Good lighting, no shadows
   - Front-facing, neutral expression

2. **Multiple Photos Per Student**:
   - Currently supports 1 photo per student
   - For better accuracy, you can modify code to support multiple photos

3. **Database Management**:
   - Regularly backup `face_encodings.pkl` and `students.json`
   - Clean up deleted student photos from `face_database/`

## Security Considerations

- Face database files contain biometric data
- Store securely and comply with privacy regulations
- Consider encryption for production deployments
- Implement access controls for enrollment interface

## Future Enhancements

Potential improvements:
- Multiple photos per student for better accuracy
- Anti-spoofing (liveness detection)
- Attendance history and analytics
- Integration with student management systems
- Mobile app for enrollment
- GPU acceleration for faster processing

## Support

For issues or questions:
1. Check console logs for error messages
2. Verify all dependencies are installed
3. Ensure camera is accessible
4. Check file permissions for database files
