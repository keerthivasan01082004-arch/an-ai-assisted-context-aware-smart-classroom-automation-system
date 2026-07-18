"""
Quick test to verify IP Webcam connection
"""
import cv2

CAMERA_URL = "http://10.132.236.41:8080/video"

print("Testing camera connection...")
print(f"Camera URL: {CAMERA_URL}")

cap = cv2.VideoCapture(CAMERA_URL)

if not cap.isOpened():
    print("❌ ERROR: Cannot connect to camera!")
    print("\nTroubleshooting:")
    print("1. Check if IP Webcam app is running on your phone")
    print("2. Verify the IP address: http://10.132.236.41:8080")
    print("3. Make sure phone and laptop are on the same WiFi")
    print("4. Try opening http://10.132.236.41:8080 in your browser")
else:
    print("✅ Camera connected successfully!")
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame captured! Size: {frame.shape}")
        print("\nCamera is working correctly!")
    else:
        print("❌ ERROR: Cannot read frame from camera")
    
    cap.release()

print("\nTest complete.")
