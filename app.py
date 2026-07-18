from flask import Flask, render_template, jsonify, request, redirect, Response, send_file
import threading
import os
import json
from datetime import datetime
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from state import state
from modules.ocr_module import parse_timetable_image, detect_subject_from_image, get_raw_ocr_output
from modules.camera_module import generate_frames, set_camera_zoom, set_camera_pan, reset_camera
from modules.realtime_engine import realtime_loop

# Try to import face recognition, but make it optional
try:
    from modules.face_recognition_module import face_recognition_system
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("⚠️ Face recognition not available. Install with: pip install face-recognition")
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition_system = None

app = Flask(__name__)
os.makedirs("static", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("attendance", exist_ok=True)
os.makedirs("face_database", exist_ok=True)
os.makedirs("uploads", exist_ok=True)


# ==============================
# Dashboard Route
# ==============================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ==============================
# Timetable Management Page
# ==============================
@app.route("/timetable")
def timetable_page():
    return render_template("timetable.html")


@app.route("/timetable/editor")
def timetable_editor():
    """Timetable editor page"""
    return render_template("timetable_editor.html")


@app.route("/timetable/data", methods=["GET"])
def get_timetable_data():
    """Get current timetable data"""
    try:
        with open("timetable_map.json", "r") as f:
            data = json.load(f)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/timetable/save", methods=["POST"])
def save_timetable():
    """Save timetable data"""
    try:
        data = request.json
        
        # Validate: Don't save if all days are empty
        total_classes = sum(len(classes) for classes in data.values())
        if total_classes == 0:
            return jsonify({"success": False, "error": "Cannot save empty timetable"}), 400
        
        with open("timetable_map.json", "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"success": True, "message": "Timetable saved successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================
# Upload Timetable Route
# ==============================
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("timetable")

    if file and file.filename != "":
        path = os.path.join("static", "timetable.png")
        file.save(path)

        # ⚠️ OCR parsing disabled - using manual timetable_map.json
        # Uncomment below to enable automatic OCR extraction
        # try:
        #     parse_timetable_image()
        #     print("✅ Timetable uploaded and parsed successfully")
        # except Exception as e:
        #     print(f"❌ Error parsing timetable: {e}")
        #     import traceback
        #     traceback.print_exc()
        
        print("✅ Timetable image uploaded (OCR disabled, using manual data)")

    return redirect("/timetable?uploaded=1")




@app.route("/view_extracted_data")
def view_extracted_data():
    """
    View the extracted timetable data in a formatted way
    """
    try:
        with open("timetable_map.json", "r") as f:
            data = json.load(f)
        
        html = """
        <html>
        <head>
            <style>
                body { background:#0f172a; color:#e2e8f0; font-family:Arial; padding:20px; }
                h1 { color:#3b82f6; }
                .day-section { 
                    background:rgba(59,130,246,0.1); 
                    border:1px solid rgba(59,130,246,0.3); 
                    border-radius:12px; 
                    padding:20px; 
                    margin:20px 0; 
                }
                .day-title { color:#64b5f6; font-size:1.5em; margin-bottom:15px; }
                .class-item { 
                    background:rgba(16,185,129,0.1); 
                    border-left:4px solid #10b981; 
                    padding:10px; 
                    margin:10px 0; 
                    border-radius:8px; 
                }
                .time { color:#10b981; font-weight:bold; }
                .course { color:#3b82f6; font-size:1.2em; font-weight:bold; }
                .details { color:#94a3b8; margin-top:5px; }
                .nav { margin:20px 0; }
                .nav a { 
                    color:#3b82f6; 
                    text-decoration:none; 
                    padding:10px 20px; 
                    background:rgba(59,130,246,0.2); 
                    border-radius:8px; 
                    margin-right:10px; 
                }
                .nav a:hover { background:rgba(59,130,246,0.3); }
                .json-view { 
                    background:#1e293b; 
                    padding:20px; 
                    border-radius:8px; 
                    overflow-x:auto; 
                    margin:20px 0; 
                }
                pre { color:#e2e8f0; }
            </style>
        </head>
        <body>
            <h1>📊 Extracted Timetable Data</h1>
            <div class="nav">
                <a href="/timetable">← Back to Timetable</a>
                <a href="/view_raw_ocr">📄 View Raw OCR</a>
                <a href="/">🏠 Dashboard</a>
            </div>
        """
        
        # Display formatted data
        total_classes = 0
        for day, classes in data.items():
            if classes:
                html += f"""
                <div class="day-section">
                    <div class="day-title">📅 {day}</div>
                """
                for cls in classes:
                    total_classes += 1
                    html += f"""
                    <div class="class-item">
                        <span class="time">⏰ {cls['start']} - {cls['end']}</span>
                        <div class="course">📘 {cls['course']}</div>
                        <div class="details">
                            🎓 Type: {cls['type']} | 
                            📍 Venue: {cls['venue']} | 
                            👥 Slot: {cls['slot']}
                        </div>
                    </div>
                    """
                html += "</div>"
        
        html += f"""
            <div style="background:rgba(16,185,129,0.2); padding:20px; border-radius:12px; margin:20px 0;">
                <h2>📈 Summary</h2>
                <p>✅ Total classes extracted: <strong>{total_classes}</strong></p>
                <p>📅 Days with classes: <strong>{len([d for d, c in data.items() if c])}</strong></p>
            </div>
            
            <h2>📄 Raw JSON Data</h2>
            <div class="json-view">
                <pre>{json.dumps(data, indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except FileNotFoundError:
        return """
        <html>
        <body style="background:#0f172a; color:#e2e8f0; font-family:Arial; padding:20px;">
            <h1>❌ No Data Found</h1>
            <p>Please upload a timetable image first.</p>
            <a href="/timetable" style="color:#3b82f6;">Go to Timetable Page</a>
        </body>
        </html>
        """, 404


@app.route("/view_raw_ocr")
def view_raw_ocr():
    """
    View raw OCR output before structured parsing
    Shows transparency in extraction process
    """
    try:
        raw_data = get_raw_ocr_output()
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ background:#0f172a; color:#e2e8f0; font-family:Arial; padding:20px; }}
                h1 {{ color:#3b82f6; }}
                h2 {{ color:#10b981; margin-top:30px; }}
                .nav {{ margin:20px 0; }}
                .nav a {{ 
                    color:#3b82f6; 
                    text-decoration:none; 
                    padding:10px 20px; 
                    background:rgba(59,130,246,0.2); 
                    border-radius:8px; 
                    margin-right:10px; 
                }}
                .nav a:hover {{ background:rgba(59,130,246,0.3); }}
                .section {{
                    background:rgba(59,130,246,0.1);
                    border:1px solid rgba(59,130,246,0.3);
                    border-radius:12px;
                    padding:20px;
                    margin:20px 0;
                }}
                .raw-text {{
                    background:#1e293b;
                    padding:20px;
                    border-radius:8px;
                    overflow-x:auto;
                    white-space:pre-wrap;
                    font-family:monospace;
                    max-height:500px;
                    overflow-y:auto;
                }}
                .timestamp {{ color:#64b5f6; font-size:0.9em; }}
                .method-result {{
                    background:rgba(16,185,129,0.1);
                    border-left:4px solid #10b981;
                    padding:15px;
                    margin:10px 0;
                    border-radius:8px;
                }}
                .red-highlight {{
                    background:rgba(239,68,68,0.2);
                    border-left:4px solid #ef4444;
                    padding:15px;
                    margin:10px 0;
                    border-radius:8px;
                }}
            </style>
        </head>
        <body>
            <h1>📄 Raw OCR Output - Extraction Transparency</h1>
            <div class="nav">
                <a href="/timetable">← Back to Timetable</a>
                <a href="/view_extracted_data">📊 View Structured Data</a>
                <a href="/">🏠 Dashboard</a>
            </div>
            
            <div class="section">
                <p class="timestamp">⏰ Extraction Time: {raw_data.get('extraction_timestamp', 'N/A')}</p>
            </div>
            
            <h2>🔴 Red Highlighted Regions (Visual Context)</h2>
            <div class="red-highlight">
                <p><strong>Red regions indicate active/important classes</strong></p>
                <div class="raw-text">{raw_data.get('red_region_text', 'No red regions detected')}</div>
            </div>
            
            <h2>📝 Full Image OCR Output</h2>
            <div class="section">
                <div class="raw-text">{raw_data.get('full_text', 'No text extracted')[:5000]}</div>
            </div>
            
            <h2>🔧 Preprocessing Methods Results</h2>
        """
        
        for result in raw_data.get('preprocessing_results', []):
            html += f"""
            <div class="method-result">
                <strong>Method:</strong> {result.get('method', 'Unknown')}<br>
                <strong>Text Length:</strong> {result.get('text_length', 0)} characters<br>
                <strong>Preview:</strong>
                <div class="raw-text" style="max-height:200px; margin-top:10px;">
                    {result.get('preview', 'No preview')}
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <html>
        <body style="background:#0f172a; color:#e2e8f0; font-family:Arial; padding:20px;">
            <h1>❌ Error Loading Raw OCR Data</h1>
            <p>Error: {str(e)}</p>
            <p>Please upload a timetable image first.</p>
            <a href="/timetable" style="color:#3b82f6;">Go to Timetable Page</a>
        </body>
        </html>
        """, 500


# ==============================
# Real-Time Data API
# ==============================
@app.route("/data")
def data():
    subject, class_type, venue = detect_subject_from_image()

    return jsonify({
        "subject": subject,
        "class_type": class_type,
        "venue": venue,
        "people": state["people"],
        "comfort": state["comfort"],
        "context": state["context"],
        "actions": state["actions"],
        "attendance": state["attendance"],
        "camera_online": state["camera_online"],
        "anomalies": state.get("anomalies", []),
        "recommendations": state.get("recommendations", []),
        "statistics": state.get("statistics", {}),
        "notifications": state.get("notifications", [])
    })


# ==============================
# Video Feed Route
# ==============================
@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ==============================
# Manual Override Controls
# ==============================
@app.route("/control", methods=["POST"])
def manual_control():
    data = request.json
    device = data.get("device")
    action = data.get("action")
    
    if device in ["lights", "fan", "ac"]:
        state["actions"][device] = action
        state["actions"]["mode"] = "🔧 Manual Override"
        return jsonify({"success": True, "message": f"{device} set to {action}"})
    
    return jsonify({"success": False, "message": "Invalid device"}), 400


# ==============================
# Camera Controls
# ==============================
@app.route("/camera/zoom", methods=["POST"])
def camera_zoom():
    """Control camera zoom"""
    data = request.json
    action = data.get("action")
    
    from modules.camera_module import camera_zoom as current_zoom
    
    if action == "in":
        new_zoom = min(3.0, current_zoom + 0.2)
        set_camera_zoom(new_zoom)
        return jsonify({"success": True, "zoom": new_zoom, "message": f"Zoomed in to {new_zoom:.1f}x"})
    elif action == "out":
        new_zoom = max(1.0, current_zoom - 0.2)
        set_camera_zoom(new_zoom)
        return jsonify({"success": True, "zoom": new_zoom, "message": f"Zoomed out to {new_zoom:.1f}x"})
    elif action == "reset":
        reset_camera()
        return jsonify({"success": True, "zoom": 1.0, "message": "Camera reset to default"})
    
    return jsonify({"success": False, "message": "Invalid action"}), 400


@app.route("/camera/pan", methods=["POST"])
def camera_pan():
    """Control camera pan"""
    data = request.json
    direction = data.get("direction")
    
    from modules.camera_module import camera_pan_x, camera_pan_y
    
    pan_step = 50  # pixels
    
    if direction == "up":
        set_camera_pan(camera_pan_x, camera_pan_y - pan_step)
        return jsonify({"success": True, "message": "Panned up"})
    elif direction == "down":
        set_camera_pan(camera_pan_x, camera_pan_y + pan_step)
        return jsonify({"success": True, "message": "Panned down"})
    elif direction == "left":
        set_camera_pan(camera_pan_x - pan_step, camera_pan_y)
        return jsonify({"success": True, "message": "Panned left"})
    elif direction == "right":
        set_camera_pan(camera_pan_x + pan_step, camera_pan_y)
        return jsonify({"success": True, "message": "Panned right"})
    
    return jsonify({"success": False, "message": "Invalid direction"}), 400


# ==============================
# Export Reports
# ==============================
@app.route("/export/csv")
def export_csv():
    """Export current statistics as CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Smart Classroom Report"])
    writer.writerow(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])
    
    # Current Status
    writer.writerow(["Current Status"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Students", state["people"]])
    writer.writerow(["Temperature", f"{state['context']['temperature']}°C"])
    writer.writerow(["Noise", f"{state['context']['noise']} dB"])
    writer.writerow(["CO2", f"{state['context']['co2']} ppm"])
    writer.writerow(["Humidity", f"{state['context']['humidity']}%"])
    writer.writerow(["Comfort Score", f"{state['comfort']}%"])
    writer.writerow(["Air Quality", state['context']['air_quality']])
    writer.writerow([])
    
    # Statistics
    stats = state.get("statistics", {})
    writer.writerow(["Daily Statistics"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Average Occupancy", stats.get("avg_occupancy", 0)])
    writer.writerow(["Peak Occupancy", stats.get("peak_occupancy", 0)])
    writer.writerow(["Total Energy", f"{stats.get('total_energy_today', 0)} kWh"])
    writer.writerow(["Energy Cost", f"₹{stats.get('energy_cost_today', 0)}"])
    writer.writerow(["Energy Saved", f"{stats.get('energy_saved', 0)} kWh"])
    writer.writerow(["Savings Percentage", f"{stats.get('savings_percentage', 0)}%"])
    writer.writerow(["CO2 Emissions", f"{stats.get('co2_emissions_kg', 0)} kg"])
    writer.writerow(["System Uptime", f"{stats.get('uptime_hours', 0)} hours"])
    writer.writerow([])
    
    # Attendance
    writer.writerow(["Attendance"])
    for student in state.get("attendance", []):
        writer.writerow([student])
    
    # Create response
    output.seek(0)
    filename = f"classroom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@app.route("/export/pdf")
def export_pdf():
    """Export current statistics as PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Smart Classroom AI - System Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Timestamp
    timestamp = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    elements.append(timestamp)
    elements.append(Spacer(1, 0.3*inch))
    
    # Current Status Table
    status_data = [
        ["Current Status", ""],
        ["Students", str(state["people"])],
        ["Temperature", f"{state['context']['temperature']}°C"],
        ["Noise Level", f"{state['context']['noise']} dB"],
        ["CO2 Level", f"{state['context']['co2']} ppm"],
        ["Humidity", f"{state['context']['humidity']}%"],
        ["Comfort Score", f"{state['comfort']}%"],
        ["Air Quality", state['context']['air_quality']],
    ]
    
    status_table = Table(status_data, colWidths=[3*inch, 2*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(status_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Statistics Table
    stats = state.get("statistics", {})
    stats_data = [
        ["Daily Statistics", ""],
        ["Average Occupancy", str(stats.get("avg_occupancy", 0))],
        ["Peak Occupancy", str(stats.get("peak_occupancy", 0))],
        ["Total Energy", f"{stats.get('total_energy_today', 0)} kWh"],
        ["Energy Cost", f"₹{stats.get('energy_cost_today', 0)}"],
        ["Energy Saved", f"{stats.get('energy_saved', 0)} kWh ({stats.get('savings_percentage', 0)}%)"],
        ["CO2 Emissions", f"{stats.get('co2_emissions_kg', 0)} kg"],
        ["Productivity Score", f"{stats.get('productivity_score', 0)}%"],
        ["System Uptime", f"{stats.get('uptime_hours', 0)} hours"],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(stats_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"classroom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@app.route("/export/attendance")
def export_attendance():
    """Export attendance as Excel file with professional formatting"""
    
    # Create workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance"
    
    # Get current data
    subject, class_type, venue = detect_subject_from_image()
    current_time = datetime.now()
    attendance_list = state.get("attendance", [])
    
    # Define styles
    header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=14)
    title_font = Font(bold=True, size=16, color="1E293B")
    info_font = Font(size=11, color="475569")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')
    
    # Title Section
    ws.merge_cells('A1:E1')
    ws['A1'] = "🏫 Smart Classroom AI - Attendance Sheet"
    ws['A1'].font = title_font
    ws['A1'].alignment = center_align
    
    # Info Section
    ws['A3'] = "Date:"
    ws['B3'] = current_time.strftime("%Y-%m-%d")
    ws['A4'] = "Time:"
    ws['B4'] = current_time.strftime("%H:%M:%S")
    ws['A5'] = "Subject:"
    ws['B5'] = subject
    ws['A6'] = "Class Type:"
    ws['B6'] = class_type
    ws['A7'] = "Total Students:"
    ws['B7'] = len(attendance_list)
    
    # Style info section
    for row in range(3, 8):
        ws[f'A{row}'].font = Font(bold=True, size=11)
        ws[f'B{row}'].font = info_font
    
    # Attendance Table Header
    header_row = 9
    headers = ["S.No", "Student ID", "Status", "Time Detected", "Remarks"]
    
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = border
    
    # Attendance Data
    data_start_row = header_row + 1
    
    if attendance_list:
        for idx, student in enumerate(attendance_list, start=1):
            row = data_start_row + idx - 1
            
            # S.No
            ws.cell(row=row, column=1, value=idx)
            ws.cell(row=row, column=1).alignment = center_align
            ws.cell(row=row, column=1).border = border
            
            # Student ID
            ws.cell(row=row, column=2, value=student)
            ws.cell(row=row, column=2).alignment = left_align
            ws.cell(row=row, column=2).border = border
            
            # Status (Present with checkmark)
            ws.cell(row=row, column=3, value="✓ Present")
            ws.cell(row=row, column=3).font = Font(color="10B981", bold=True)
            ws.cell(row=row, column=3).alignment = center_align
            ws.cell(row=row, column=3).border = border
            
            # Time Detected
            ws.cell(row=row, column=4, value=current_time.strftime("%H:%M:%S"))
            ws.cell(row=row, column=4).alignment = center_align
            ws.cell(row=row, column=4).border = border
            
            # Remarks (empty for manual entry)
            ws.cell(row=row, column=5, value="")
            ws.cell(row=row, column=5).border = border
    else:
        # No students detected
        ws.merge_cells(f'A{data_start_row}:E{data_start_row}')
        ws[f'A{data_start_row}'] = "No students detected"
        ws[f'A{data_start_row}'].font = Font(italic=True, color="94A3B8")
        ws[f'A{data_start_row}'].alignment = center_align
    
    # Summary Section
    summary_row = data_start_row + len(attendance_list) + 2
    
    ws[f'A{summary_row}'] = "Summary Statistics"
    ws[f'A{summary_row}'].font = Font(bold=True, size=12)
    
    stats = state.get("statistics", {})
    summary_data = [
        ("Total Present:", len(attendance_list)),
        ("Comfort Score:", f"{state.get('comfort', 0)}%"),
        ("Temperature:", f"{state['context'].get('temperature', 0)}°C"),
        ("Air Quality:", state['context'].get('air_quality', 'N/A')),
        ("Productivity Score:", f"{stats.get('productivity_score', 0)}%"),
    ]
    
    for idx, (label, value) in enumerate(summary_data):
        row = summary_row + idx + 1
        ws[f'A{row}'] = label
        ws[f'B{row}'] = value
        ws[f'A{row}'].font = Font(bold=True, size=10)
        ws[f'B{row}'].font = Font(size=10)
    
    # Footer
    footer_row = summary_row + len(summary_data) + 3
    ws.merge_cells(f'A{footer_row}:E{footer_row}')
    ws[f'A{footer_row}'] = f"Generated by Smart Classroom AI System | {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
    ws[f'A{footer_row}'].font = Font(size=9, italic=True, color="64748B")
    ws[f'A{footer_row}'].alignment = center_align
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 30
    
    # Save to BytesIO
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)
    
    filename = f"attendance_{current_time.strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


# ==============================
# Historical Data API
# ==============================
@app.route("/history")
def get_history():
    """Get historical data for charts"""
    from modules.realtime_engine import occupancy_history, energy_history, comfort_history
    
    return jsonify({
        "occupancy": list(occupancy_history),
        "energy": list(energy_history),
        "comfort": list(comfort_history),
        "timestamps": [i * 5 for i in range(len(occupancy_history))]  # 5-minute intervals
    })


# ==============================
# Face Recognition Routes
# ==============================

@app.route("/attendance")
def attendance_page():
    """Dedicated attendance page with face recognition camera"""
    return render_template("attendance.html")


@app.route("/attendance/video_feed")
def attendance_video_feed():
    """Separate video feed for attendance (always uses face recognition)"""
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/attendance/data")
def attendance_data():
    """Get current attendance data"""
    subject, class_type, venue = detect_subject_from_image()
    
    # Get enrolled students count
    enrolled_count = 0
    if FACE_RECOGNITION_AVAILABLE and face_recognition_system:
        enrolled_count = len(face_recognition_system.list_enrolled_students())
    
    present_count = len(state.get("attendance", []))
    attendance_rate = f"{(present_count / enrolled_count * 100):.1f}%" if enrolled_count > 0 else "0%"
    
    # Add timestamps to attendance
    attendance_with_time = []
    for student in state.get("attendance", []):
        if isinstance(student, dict):
            student_copy = student.copy()
            if 'time' not in student_copy:
                student_copy['time'] = datetime.now().strftime("%H:%M:%S")
            attendance_with_time.append(student_copy)
        else:
            attendance_with_time.append({
                "id": student,
                "name": student,
                "confidence": 1.0,
                "time": datetime.now().strftime("%H:%M:%S")
            })
    
    return jsonify({
        "attendance": attendance_with_time,
        "present_count": present_count,
        "total_enrolled": enrolled_count,
        "attendance_rate": attendance_rate,
        "current_class": subject if subject != "No Class" else "Free Period"
    })


@app.route("/attendance/clear", methods=["POST"])
def clear_attendance():
    """Clear today's attendance"""
    state["attendance"] = []
    state["people"] = 0
    return jsonify({"success": True, "message": "Attendance cleared"})


@app.route("/face/enroll")
def face_enroll_page():
    """Face enrollment page"""
    if not FACE_RECOGNITION_AVAILABLE:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Face Recognition Not Available</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="container" style="max-width: 800px; margin: 50px auto; padding: 40px;">
                <div class="glass-card" style="text-align: center; padding: 40px;">
                    <div style="font-size: 5em; margin-bottom: 20px;">⚠️</div>
                    <h1 style="color: #f59e0b; margin-bottom: 20px;">Face Recognition Not Available</h1>
                    <p style="color: #94a3b8; font-size: 1.1em; margin-bottom: 30px;">
                        The face recognition library is not installed on your system.
                    </p>
                    
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0; text-align: left;">
                        <h3 style="color: #ef4444; margin-bottom: 15px;">📋 Installation Required:</h3>
                        <p style="color: #cbd5e1; margin-bottom: 10px;">1. Install CMake from <a href="https://cmake.org/download/" target="_blank" style="color: #3b82f6;">cmake.org</a></p>
                        <p style="color: #cbd5e1; margin-bottom: 10px;">2. Restart your terminal</p>
                        <p style="color: #cbd5e1; margin-bottom: 10px;">3. Run this command:</p>
                        <div style="background: #1e293b; padding: 15px; border-radius: 8px; margin-top: 10px;">
                            <code style="color: #10b981; font-size: 1.1em;">pip install face-recognition dlib numpy</code>
                        </div>
                    </div>
                    
                    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0; text-align: left;">
                        <h3 style="color: #3b82f6; margin-bottom: 15px;">ℹ️ Current Status:</h3>
                        <p style="color: #cbd5e1;">✅ System is using YOLO person detection (generic Student_001, Student_002, etc.)</p>
                        <p style="color: #cbd5e1;">❌ Face recognition with student names is disabled</p>
                        <p style="color: #cbd5e1; margin-top: 10px;">Once you install the library, face recognition will automatically activate!</p>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <a href="/" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-right: 10px;">
                            🏠 Back to Dashboard
                        </a>
                        <a href="https://github.com/ageitgey/face_recognition#installation" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                            📖 Installation Guide
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    return render_template("face_enroll.html")


@app.route("/face/students", methods=["GET"])
def get_enrolled_students():
    """Get list of enrolled students"""
    if not FACE_RECOGNITION_AVAILABLE:
        return jsonify({"success": False, "error": "Face recognition not available"}), 503
    students = face_recognition_system.list_enrolled_students()
    return jsonify({"success": True, "students": students})


@app.route("/face/enroll", methods=["POST"])
def enroll_student():
    """Enroll a new student with face recognition"""
    if not FACE_RECOGNITION_AVAILABLE:
        return jsonify({"success": False, "error": "Face recognition not available"}), 503
    
    try:
        student_id = request.form.get("student_id")
        student_name = request.form.get("student_name")
        photo = request.files.get("photo")
        
        if not student_id or not student_name or not photo:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Save uploaded photo
        photo_path = os.path.join("face_database", f"{student_id}.jpg")
        photo.save(photo_path)
        
        # Enroll student
        success = face_recognition_system.enroll_student(student_id, student_name, photo_path)
        
        if success:
            return jsonify({"success": True, "message": f"Student {student_name} enrolled successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to detect face in photo"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/face/delete/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Delete a student from face recognition database"""
    if not FACE_RECOGNITION_AVAILABLE:
        return jsonify({"success": False, "error": "Face recognition not available"}), 503
    
    try:
        success = face_recognition_system.delete_student(student_id)
        if success:
            return jsonify({"success": True, "message": f"Student {student_id} deleted"})
        else:
            return jsonify({"success": False, "error": "Student not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/face/reload", methods=["POST"])
def reload_face_database():
    """Reload face recognition database"""
    if not FACE_RECOGNITION_AVAILABLE:
        return jsonify({"success": False, "error": "Face recognition not available"}), 503
    
    try:
        face_recognition_system.load_face_database()
        return jsonify({"success": True, "message": "Face database reloaded"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================
# Main Entry
# ==============================
if __name__ == "__main__":
    threading.Thread(target=realtime_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
