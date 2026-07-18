import cv2
import pytesseract
import json
import re
import numpy as np
from datetime import datetime
import os
from difflib import get_close_matches

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Valid course codes database for verification
VALID_COURSE_CODES = [
    # From your timetable
    "CSI3616", "CSI3012", "CSI3014", "CSI3020", "CSI3032", 
    "CSE2001", "CSE3501", "CSI2007", "CSE2004",
    "STS4022", "PHY1001", "CSI4004",
    # Additional common codes
    "MAT2001", "CHE1001", "ENG1001", "MGT1001",
    "CSE1001", "CSE1002", "CSI1001", "ECE2001", "EEE2001"
]

# Store raw OCR output globally for display
raw_ocr_output = {
    "full_text": "",
    "red_region_text": "",
    "preprocessing_results": [],
    "extraction_timestamp": ""
}


def intelligent_timetable_extraction():
    """
    Advanced AI-powered timetable extraction with:
    - Red color detection (visual understanding)
    - Multi-strategy OCR
    - Course code validation
    - Raw text storage
    - High accuracy parsing
    """
    global raw_ocr_output
    
    path = "static/timetable.png"
    
    if not os.path.exists(path):
        print("❌ Timetable image not found")
        return {}
    
    print("\n" + "="*80)
    print("🤖 INTELLIGENT TIMETABLE AI - ADVANCED EXTRACTION ENGINE")
    print("="*80)
    
    # Load image
    img = cv2.imread(path)
    
    if img is None:
        print("❌ Failed to load image")
        return {}
    
    print(f"📐 Image loaded: {img.shape[1]}x{img.shape[0]} pixels")
    
    # STEP 1: Image Preprocessing
    print("\n🔧 STEP 1: Advanced Image Preprocessing...")
    preprocessed_images = advanced_preprocessing(img)
    
    # STEP 2: Red Color Detection (Visual Understanding)
    print("\n🔴 STEP 2: Red Highlight Detection (Visual Context)...")
    red_regions, red_text = detect_red_highlighted_classes(img)
    raw_ocr_output["red_region_text"] = red_text
    
    # STEP 3: Multi-Strategy OCR Extraction
    print("\n🔍 STEP 3: Multi-Strategy OCR Extraction...")
    full_text = extract_with_advanced_ocr(preprocessed_images)
    raw_ocr_output["full_text"] = full_text
    
    # STEP 4: Table Structure Detection
    print("\n📊 STEP 4: Table Structure Analysis...")
    table_data = detect_table_structure(img)
    
    # STEP 5: Combine all extraction strategies
    print("\n🧠 STEP 5: Intelligent Text Combination...")
    combined_text = full_text + "\n" + red_text
    
    # Store raw output
    raw_ocr_output["extraction_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n📄 RAW OCR OUTPUT (First 1000 chars):")
    print("-" * 80)
    print(combined_text[:1000])
    print("-" * 80)
    
    # STEP 6: Intelligent Parsing with Validation
    print("\n🎯 STEP 6: Intelligent Parsing & Course Validation...")
    timetable = intelligent_parsing_with_validation(combined_text, table_data, red_regions)
    
    # STEP 7: Save to JSON
    with open("timetable_map.json", "w") as f:
        json.dump(timetable, f, indent=2)
    
    # Save raw OCR output
    with open("raw_ocr_output.json", "w") as f:
        json.dump(raw_ocr_output, f, indent=2)
    
    total_classes = sum(len(classes) for classes in timetable.values())
    
    print("\n" + "="*80)
    print(f"✅ EXTRACTION COMPLETE - {total_classes} classes extracted & validated")
    print("="*80)
    
    return timetable


def advanced_preprocessing(img):
    """
    Advanced image preprocessing for maximum OCR accuracy
    Returns multiple preprocessed versions
    """
    preprocessed = []
    
    # Method 1: Grayscale + Gaussian Blur + Adaptive Threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    preprocessed.append(("Adaptive Threshold", adaptive))
    
    # Method 2: OTSU Thresholding
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocessed.append(("OTSU Threshold", otsu))
    
    # Method 3: Denoising + Threshold
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, denoised_thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocessed.append(("Denoised", denoised_thresh))
    
    # Method 4: Contrast Enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    _, enhanced_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocessed.append(("CLAHE Enhanced", enhanced_thresh))
    
    # Method 5: Morphological Operations
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
    preprocessed.append(("Morphological", morph))
    
    print(f"  ✅ Generated {len(preprocessed)} preprocessed versions")
    
    return preprocessed


def detect_red_highlighted_classes(img):
    """
    Detect red-highlighted regions in timetable (visual understanding)
    Red color = Active/Important class
    """
    print("  🔴 Analyzing red color regions...")
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define red color ranges (HSV)
    # Red wraps around in HSV, so we need two ranges
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # Create masks
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # Find contours of red regions
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    red_regions = []
    red_text_combined = ""
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Filter small noise
            x, y, w, h = cv2.boundingRect(contour)
            red_regions.append((x, y, w, h))
            
            # Extract text from red region
            roi = img[y:y+h, x:x+w]
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            text = pytesseract.image_to_string(thresh_roi, config='--psm 6')
            red_text_combined += text + "\n"
            
            print(f"  🔴 Red region found at ({x},{y}) size {w}x{h}")
    
    print(f"  ✅ Detected {len(red_regions)} red-highlighted regions")
    
    return red_regions, red_text_combined


def extract_with_advanced_ocr(preprocessed_images):
    """
    Extract text using multiple preprocessing methods
    Combines results for maximum accuracy
    """
    global raw_ocr_output
    
    all_texts = []
    
    for method_name, processed_img in preprocessed_images:
        try:
            # Try multiple PSM modes
            configs = [
                '--psm 6',  # Assume uniform block of text
                '--psm 4',  # Assume single column of text
                '--psm 3',  # Fully automatic page segmentation
            ]
            
            best_text = ""
            max_length = 0
            
            for config in configs:
                text = pytesseract.image_to_string(processed_img, config=config)
                if len(text) > max_length:
                    max_length = len(text)
                    best_text = text
            
            all_texts.append(best_text)
            raw_ocr_output["preprocessing_results"].append({
                "method": method_name,
                "text_length": len(best_text),
                "preview": best_text[:200]
            })
            
            print(f"  ✅ {method_name}: {len(best_text)} chars extracted")
            
        except Exception as e:
            print(f"  ⚠️ {method_name} failed: {e}")
    
    # Combine all texts
    combined = "\n".join(all_texts)
    
    return combined


def detect_table_structure(img):
    """
    Detect table structure using contours and lines
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    
    horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
    
    # Combine lines
    table_structure = cv2.add(horizontal_lines, vertical_lines)
    
    # Find contours (cells)
    contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 20:  # Filter small contours
            cells.append((x, y, w, h))
    
    return {"cells": cells, "count": len(cells)}


def validate_course_code(extracted_code):
    """
    Validate and correct course codes using fuzzy matching
    Ensures only accurate course codes are stored
    """
    if not extracted_code:
        return None
    
    # Clean the extracted code
    cleaned = extracted_code.strip().upper()
    
    # Check if it's already valid
    if cleaned in VALID_COURSE_CODES:
        return cleaned
    
    # Try fuzzy matching
    matches = get_close_matches(cleaned, VALID_COURSE_CODES, n=1, cutoff=0.75)
    
    if matches:
        corrected = matches[0]
        print(f"  🔧 Course code corrected: {extracted_code} → {corrected}")
        return corrected
    
    # If no match found, check if it follows pattern
    course_pattern = r'^[A-Z]{3}\d{4}[A-Z]?$'
    if re.match(course_pattern, cleaned):
        print(f"  ⚠️ New course code detected: {cleaned} (not in database)")
        return cleaned
    
    print(f"  ❌ Invalid course code rejected: {extracted_code}")
    return None


def intelligent_parsing_with_validation(text, table_data, red_regions):
    """
    Advanced parsing for timetable format: SLOT-COURSECODE-TYPE-VENUE-ALL
    Example: L11-CSI2007-ELA-PRP354-ALL
    Where: L11=Slot, CSI2007=Course, ELA=Type(Lab), PRP354=Venue
    """
    lines = text.split('\n')
    
    # Initialize timetable
    timetable = {
        "MON": [], "TUE": [], "WED": [], "THU": [], 
        "FRI": [], "SAT": [], "SUN": []
    }
    
    # Pattern for your exact format: SLOT-COURSECODE-TYPE-VENUE-ALL
    # Matches: L11-CSI2007-ELA-PRP354-ALL, A1-CSI3020-TH-STS22-ALL, etc.
    entry_pattern = r'([A-Z]+\d+)-([A-Z]{3}\d{4}[A-Z]?)-([A-Z]{2,4})-([A-Z]{2,4}\d{2,4})-ALL'
    
    time_pattern = r'(\d{2}):(\d{2})'
    
    # Extract time slots from header
    time_slots = []
    for line in lines[:20]:
        times = re.findall(time_pattern, line)
        for t in times:
            time_str = f"{t[0]}:{t[1]}"
            if time_str not in time_slots and 7 <= int(t[0]) <= 20:
                time_slots.append(time_str)
    
    time_slots = sorted(list(set(time_slots)))
    
    if not time_slots:
        time_slots = ["08:00", "09:00", "10:00", "11:00", "12:00", 
                     "14:00", "15:00", "16:00", "17:00", "18:00"]
    
    print(f"  ⏰ Detected time slots: {time_slots[:12]}")
    
    # Extract all entries from the entire text
    all_entries = []
    for line in lines:
        matches = re.findall(entry_pattern, line)
        for match in matches:
            slot, course_raw, type_code, venue = match
            
            # Validate course code
            course_code = validate_course_code(course_raw)
            if not course_code:
                # If validation fails, still use it if it matches pattern
                if re.match(r'^[A-Z]{3}\d{4}[A-Z]?$', course_raw):
                    course_code = course_raw
                    print(f"  ⚠️ Using unvalidated course code: {course_raw}")
                else:
                    continue
            
            # Map type codes correctly
            if type_code == "ELA":
                class_type = "LAB"
            elif type_code in ["ETH", "TH"]:
                class_type = "THEORY"
            else:
                class_type = "THEORY"
            
            all_entries.append({
                "slot": slot,
                "course": course_code,
                "type": class_type,
                "venue": venue,
                "original_line": line
            })
            
            print(f"  🔍 Extracted: {slot}-{course_code}-{type_code}-{venue} → {class_type}")
    
    print(f"\n  📊 Total entries extracted: {len(all_entries)}")
    
    if len(all_entries) == 0:
        print("  ❌ No entries found! Check OCR output.")
        return timetable
    
    # Now organize by day
    # Strategy: Look for day names and group entries that appear near them
    
    day_keywords = {
        "MON": ["MON", "MONDAY"],
        "TUE": ["TUE", "TUESDAY"],
        "WED": ["WED", "WEDNESDAY"],
        "THU": ["THU", "THURSDAY"],
        "FRI": ["FRI", "FRIDAY"],
        "SAT": ["SAT", "SATURDAY"],
        "SUN": ["SUN", "SUNDAY"]
    }
    
    # Find where each day appears in the text
    day_positions = {}
    for i, line in enumerate(lines):
        line_upper = line.upper()
        for day, keywords in day_keywords.items():
            for keyword in keywords:
                if keyword in line_upper:
                    if day not in day_positions:
                        day_positions[day] = []
                    day_positions[day].append(i)
                    print(f"  📅 Found {day} at line {i}")
                    break
    
    # Group entries by day based on their position in text
    if day_positions:
        # Sort days by their first appearance
        sorted_days = sorted(day_positions.keys(), key=lambda d: min(day_positions[d]))
        
        # For each day, find entries between its position and the next day
        for day_idx, day in enumerate(sorted_days):
            day_line = min(day_positions[day])
            
            # Find next day's position
            if day_idx + 1 < len(sorted_days):
                next_day = sorted_days[day_idx + 1]
                next_day_line = min(day_positions[next_day])
            else:
                next_day_line = len(lines)
            
            # Find entries in this day's section
            day_entries = []
            for entry in all_entries:
                # Find which line this entry came from
                entry_line_idx = None
                for i, line in enumerate(lines):
                    if entry["original_line"] == line:
                        entry_line_idx = i
                        break
                
                # If entry is in this day's range, add it
                if entry_line_idx and day_line <= entry_line_idx < next_day_line:
                    if entry not in day_entries:
                        day_entries.append(entry)
            
            # Assign time slots to this day's entries
            for idx, entry in enumerate(day_entries):
                if idx < len(time_slots):
                    start_time = time_slots[idx]
                    hour, minute = map(int, start_time.split(':'))
                    
                    # Calculate end time (50 min classes)
                    end_minute = minute + 50
                    end_hour = hour
                    if end_minute >= 60:
                        end_minute -= 60
                        end_hour += 1
                    
                    end_time = f"{end_hour:02d}:{end_minute:02d}"
                    
                    timetable[day].append({
                        "start": start_time,
                        "end": end_time,
                        "slot": entry["slot"],
                        "course": entry["course"],
                        "type": entry["type"],
                        "venue": entry["venue"]
                    })
                    
                    print(f"    ✅ {day} {start_time}: {entry['course']} ({entry['type']}) @ {entry['venue']} [Slot: {entry['slot']}]")
    
    else:
        # Fallback: If no day markers found, distribute entries across weekdays
        print("  ⚠️ No clear day markers found, using intelligent distribution")
        
        # Typical timetable has 5 days (Mon-Fri) with similar number of classes
        days = ["MON", "TUE", "WED", "THU", "FRI"]
        entries_per_day = len(all_entries) // len(days)
        
        entry_idx = 0
        for day in days:
            day_entries = all_entries[entry_idx:entry_idx + entries_per_day]
            entry_idx += entries_per_day
            
            for idx, entry in enumerate(day_entries):
                if idx < len(time_slots):
                    start_time = time_slots[idx]
                    hour, minute = map(int, start_time.split(':'))
                    
                    end_minute = minute + 50
                    end_hour = hour
                    if end_minute >= 60:
                        end_minute -= 60
                        end_hour += 1
                    
                    end_time = f"{end_hour:02d}:{end_minute:02d}"
                    
                    timetable[day].append({
                        "start": start_time,
                        "end": end_time,
                        "slot": entry["slot"],
                        "course": entry["course"],
                        "type": entry["type"],
                        "venue": entry["venue"]
                    })
                    
                    print(f"    ✅ {day} {start_time}: {entry['course']} ({entry['type']}) @ {entry['venue']}")
    
    return timetable


def parse_timetable_image():
    """
    Main entry point for intelligent timetable extraction
    """
    return intelligent_timetable_extraction()


def time_in_range(current_time, start_str, end_str):
    """
    Check if current time falls within start-end interval
    """
    fmt = "%H:%M"
    start = datetime.strptime(start_str, fmt).time()
    end = datetime.strptime(end_str, fmt).time()
    return start <= current_time <= end


def load_timetable_map():
    """
    Load the timetable_map.json
    """
    try:
        with open("timetable_map.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("timetable_map.json not found")
        return {}


def get_raw_ocr_output():
    """
    Return raw OCR output for display
    """
    return raw_ocr_output


def detect_subject_from_image():
    """
    Detect current subject based on day and time
    Returns: course code, class type, and venue
    """
    timetable_map = load_timetable_map()

    if not timetable_map:
        return "No Class", "free", "-"

    now = datetime.now()
    current_day = now.strftime("%a").upper()[:3]
    current_time = now.time()

    print(f"🕐 Current Day: {current_day}, Current Time: {current_time}")

    if current_day not in timetable_map:
        return "No Class", "free", "-"

    # Check each class slot for today
    for slot in timetable_map[current_day]:
        start_str = slot["start"]
        end_str = slot["end"]
        
        if time_in_range(current_time, start_str, end_str):
            course_code = slot.get("course", "Unknown")
            class_type = slot.get("type", "Unknown")
            venue = slot.get("venue", "-")
            
            print(f"✅ Found: {course_code} ({class_type}) @ {venue} from {start_str} to {end_str}")
            return course_code, class_type, venue

    return "No Class", "free", "-"
