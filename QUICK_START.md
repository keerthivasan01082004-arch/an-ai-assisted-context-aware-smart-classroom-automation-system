# 🚀 Quick Start Guide - Smart Classroom AI

## ⚡ 5-Minute Setup

### Step 1: Install Required Libraries
```bash
yolo311\Scripts\activate.bat
pip install reportlab openpyxl
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open Browser
- Dashboard: http://localhost:5000
- Timetable: http://localhost:5000/timetable

---

## 🎯 Quick Feature Tour

### 1. Main Dashboard (/)
- View real-time metrics (9 cards)
- Check AI insights (energy, cost, CO2)
- See predictive analytics
- Monitor notifications
- Control devices manually
- Export reports (CSV/PDF)
- View historical charts

### 2. Timetable Page (/timetable)
- Upload timetable image
- View current schedule
- See today's classes
- AI processes automatically

---

## 🔧 Quick Actions

### Export a Report
1. Click "Export CSV" or "Export PDF" or "Attendance Excel"
2. File downloads automatically
3. Open and share

**Attendance Excel includes:**
- Student list with timestamps
- Subject and class info
- Summary statistics
- Professional formatting
- Ready to print

### Manual Control
1. Scroll to "Manual Override Controls"
2. Click device button (Lights/Fan/AC)
3. Select state (ON/OFF/LOW/MED/HIGH)
4. See instant feedback

### Upload Timetable
1. Go to /timetable page
2. Click "Choose File"
3. Select timetable image
4. Click "Upload & Process"
5. Wait for AI processing

---

## 📊 What You'll See

### Real-Time Data (Updates every 3 seconds)
- Student count
- Temperature
- Noise level
- CO2 concentration
- Humidity
- Comfort score
- Productivity score
- Air quality
- Energy consumption

### AI Insights
- Energy cost (₹)
- CO2 emissions (kg)
- Energy saved (%)
- Average occupancy
- Peak occupancy
- Productivity score

### Predictions
- Next class details
- Class end time
- Occupancy trend
- Attention status

### Notifications
- Real-time alerts
- Color-coded by severity
- Actionable recommendations

---

## 🎨 UI Navigation

### Top Navigation Bar
- 🏠 Dashboard - Main page
- 📅 Timetable - Schedule management
- 📊 Export CSV - Download data
- 📄 Export PDF - Professional report
- 📋 Attendance Excel - Attendance sheet

### Dashboard Sections (scroll down)
1. Info Cards - Current metrics
2. AI Insights - Energy & analytics
3. Notifications - Real-time alerts
4. Predictive Analytics - Forecasts
5. Anomalies - Security alerts (if any)
6. Recommendations - AI suggestions (if any)
7. Manual Controls - Override devices
8. Automated Actions - Current status
9. Camera Feed - Live video
10. Attendance - Student list
11. Real-Time Charts - Last 10 readings
12. Historical Charts - Last 24 hours

---

## 💡 Tips

### For Best Results:
- Keep camera running
- Upload clear timetable
- Check notifications regularly
- Export reports daily
- Review historical data weekly

### Troubleshooting:
- **No camera feed?** Check camera URL in camera_module.py
- **PDF export fails?** Install reportlab: `pip install reportlab`
- **Timetable not parsing?** Use clear, high-resolution image
- **Data not updating?** Check if realtime_loop is running

---

## 🎓 Demo Sequence

### For Presentation:
1. **Start** - Show dashboard loading
2. **Metrics** - Point out 9 real-time cards
3. **AI Insights** - Explain energy tracking
4. **Predictions** - Show next class info
5. **Manual Control** - Override a device
6. **Export** - Generate PDF report
7. **History** - Show 24-hour charts
8. **Timetable** - Navigate to timetable page
9. **Features** - Highlight unique aspects
10. **Conclusion** - Summarize benefits

---

## 📱 Key Shortcuts

- **F5** - Refresh dashboard
- **Ctrl+Click** on Export - Open in new tab
- **F11** on camera - Fullscreen video
- **Ctrl+P** on PDF - Print report

---

## ✅ Checklist Before Presentation

- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Camera accessible
- [ ] Timetable uploaded
- [ ] ReportLab installed
- [ ] Application running
- [ ] Browser open to dashboard
- [ ] Data updating (check clock)
- [ ] Charts displaying
- [ ] Export buttons working

---

## 🎯 Key Points to Mention

1. **30+ Features** - Comprehensive system
2. **AI-Powered** - YOLOv8, predictions, recommendations
3. **Real-Time** - 3-second updates
4. **Sustainable** - Carbon tracking, 30-40% savings
5. **Practical** - Manual controls, export reports
6. **Professional** - Production-ready UI
7. **Scalable** - Multi-room capable

---

## 🚨 Common Issues & Fixes

### Issue: Camera offline
**Fix**: Check camera URL, ensure camera is accessible

### Issue: PDF export error
**Fix**: `pip install reportlab`

### Issue: Timetable not detected
**Fix**: Upload clearer image, check OCR path

### Issue: Data not updating
**Fix**: Check console for errors, restart app

### Issue: Charts not showing
**Fix**: Wait 10 seconds for data collection

---

## 📞 Need Help?

1. Check documentation files
2. Review error messages in console
3. Verify all dependencies installed
4. Test with sample data
5. Restart application

---

**You're all set! Your Smart Classroom AI System is ready to impress! 🎉**

**Good luck with your presentation! 🚀**
