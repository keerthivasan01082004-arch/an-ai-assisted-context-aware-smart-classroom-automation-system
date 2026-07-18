import time
import random
import json
import re
from datetime import datetime, timedelta
from state import state
from collections import deque

# Energy cost per kWh (in your local currency)
ENERGY_COST_PER_KWH = 8.5  # ₹8.5 per kWh (adjust as needed)

# System start time
SYSTEM_START_TIME = datetime.now()

# Historical data storage (last 24 hours)
occupancy_history = deque(maxlen=288)  # 24 hours * 12 (5-min intervals)
energy_history = deque(maxlen=288)
comfort_history = deque(maxlen=288)

# Peak tracking
peak_occupancy_today = 0
total_energy_consumed = 0
total_people_minutes = 0
class_sessions_today = 0


def calculate_comfort(temperature, noise, people_count, co2, humidity):
    """
    Calculate comfort score (0-100) based on environmental factors
    
    Optimal conditions:
    - Temperature: 22-26°C
    - Noise: < 40 dB
    - CO2: < 800 ppm
    - Humidity: 40-60%
    - Occupancy: Not overcrowded
    """
    comfort = 100
    
    # Temperature impact
    if temperature < 18:
        comfort -= (18 - temperature) * 5  # Too cold
    elif temperature > 26:
        comfort -= (temperature - 26) * 4  # Too hot
    
    # Noise impact
    if noise > 40:
        comfort -= (noise - 40) * 1.5  # Too noisy
    
    # CO2 impact (air quality)
    if co2 > 800:
        comfort -= (co2 - 800) * 0.02
    
    # Humidity impact
    if humidity < 40:
        comfort -= (40 - humidity) * 0.5  # Too dry
    elif humidity > 60:
        comfort -= (humidity - 60) * 0.8  # Too humid
    
    # Overcrowding impact (assuming max capacity ~50)
    if people_count > 40:
        comfort -= (people_count - 40) * 2
    
    # Ensure comfort stays in 0-100 range
    comfort = max(0, min(100, comfort))
    
    return int(comfort)


def simulate_environmental_data(people_count):
    """
    Simulate realistic environmental data based on occupancy
    In production, replace with actual sensor readings
    """
    # Base values
    base_temp = 24
    base_noise = 30
    base_co2 = 400  # ppm (outdoor level)
    base_humidity = 55
    
    # Temperature increases with more people (body heat)
    temperature = base_temp + (people_count * 0.15) + random.uniform(-1, 1)
    
    # Noise increases with more people (conversations)
    noise = base_noise + (people_count * 0.8) + random.uniform(-3, 5)
    
    # CO2 increases with more people (breathing)
    co2 = base_co2 + (people_count * 15) + random.uniform(-20, 30)
    
    # Humidity slightly increases with occupancy
    humidity = base_humidity + (people_count * 0.3) + random.uniform(-5, 5)
    
    # Air quality based on CO2 levels
    if co2 < 600:
        air_quality = "Excellent"
    elif co2 < 800:
        air_quality = "Good"
    elif co2 < 1000:
        air_quality = "Moderate"
    elif co2 < 1500:
        air_quality = "Poor"
    else:
        air_quality = "Unhealthy"
    
    return round(temperature, 1), round(noise, 1), int(co2), round(humidity, 1), air_quality


def predict_energy_consumption(people_count, temperature, actions):
    """
    AI-powered energy prediction in kWh
    """
    base_consumption = 0.5  # Base load
    
    # Lighting
    if actions["lights"] == "ON":
        base_consumption += 0.3 * (people_count / 50)
    
    # Fan consumption
    fan_power = {"OFF": 0, "LOW": 0.075, "MEDIUM": 0.15, "HIGH": 0.25}
    base_consumption += fan_power.get(actions["fan"], 0)
    
    # AC consumption (highest)
    if "ON" in actions["ac"]:
        base_consumption += 2.5 + (temperature - 22) * 0.1
    
    return round(base_consumption, 2)


def predict_next_hour_occupancy():
    """
    AI predicts occupancy for next hour based on timetable and patterns
    """
    current_hour = datetime.now().hour
    current_day = datetime.now().strftime("%a").upper()[:3]
    
    # Simple prediction based on time patterns
    if 8 <= current_hour < 18:  # Class hours
        # Peak hours: 10-12, 14-16
        if current_hour in [10, 11, 14, 15]:
            return random.randint(35, 45)
        else:
            return random.randint(20, 35)
    else:
        return random.randint(0, 5)


def calculate_productivity_score(comfort, noise, co2, temperature):
    """
    Calculate learning productivity score based on environmental factors
    Research shows optimal learning conditions
    """
    productivity = 100
    
    # Comfort directly affects productivity
    productivity = comfort * 0.4
    
    # Noise impact on concentration
    if noise < 40:
        productivity += 30  # Quiet environment
    elif noise < 55:
        productivity += 20  # Acceptable
    elif noise < 70:
        productivity += 10  # Distracting
    else:
        productivity += 0  # Very distracting
    
    # CO2 impact on cognitive function
    if co2 < 600:
        productivity += 20  # Excellent air
    elif co2 < 800:
        productivity += 15  # Good air
    elif co2 < 1000:
        productivity += 10  # Moderate
    else:
        productivity += 5  # Poor air affects cognition
    
    # Temperature impact on alertness
    if 20 <= temperature <= 24:
        productivity += 10  # Optimal
    elif 18 <= temperature <= 26:
        productivity += 5  # Acceptable
    else:
        productivity += 0  # Too hot/cold
    
    return min(100, int(productivity))


def detect_attention_patterns(people_count, noise):
    """
    Detect if class is engaged or distracted based on noise patterns
    """
    if people_count == 0:
        return "No Class"
    
    # Noise per person ratio
    noise_per_person = noise / max(people_count, 1)
    
    if noise_per_person < 1.5:
        return "🎯 Highly Focused"
    elif noise_per_person < 2.5:
        return "✅ Engaged"
    elif noise_per_person < 3.5:
        return "⚠️ Moderate Distraction"
    else:
        return "❌ High Distraction"


def calculate_energy_savings():
    """
    Calculate energy saved compared to always-on system
    """
    global total_energy_consumed
    
    # Assume always-on would consume 3 kWh constantly
    hours_running = (datetime.now() - SYSTEM_START_TIME).total_seconds() / 3600
    always_on_consumption = hours_running * 3.0
    
    savings = always_on_consumption - total_energy_consumed
    savings_percentage = (savings / max(always_on_consumption, 0.1)) * 100
    
    return round(savings, 2), round(savings_percentage, 1)


def predict_class_end_time():
    """
    Predict when current class will end based on timetable
    """
    now = datetime.now()
    current_time = now.time()
    current_day = now.strftime("%a").upper()[:3]
    
    # Common class end times
    class_end_times = ["08:50", "09:50", "10:50", "11:50", "12:50", 
                       "14:50", "15:50", "16:50", "17:50"]
    
    for end_time_str in class_end_times:
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        if current_time < end_time:
            # Calculate minutes remaining
            end_datetime = datetime.combine(now.date(), end_time)
            minutes_remaining = int((end_datetime - now).total_seconds() / 60)
            return end_time_str, minutes_remaining
    
    return "N/A", 0


def calculate_carbon_footprint(energy_kwh):
    """
    Calculate CO2 emissions from energy consumption
    Average: 0.82 kg CO2 per kWh in India
    """
    co2_kg = energy_kwh * 0.82
    
    # Trees needed to offset (1 tree absorbs ~21 kg CO2/year)
    trees_equivalent = co2_kg / (21 / 365)  # Daily equivalent
    
    return round(co2_kg, 2), round(trees_equivalent, 2)


def generate_smart_notifications(people_count, comfort, co2, temperature, anomalies):
    """
    Generate actionable real-time notifications
    """
    notifications = []
    current_time = datetime.now()
    
    # Class ending soon
    end_time, minutes_remaining = predict_class_end_time()
    if 0 < minutes_remaining <= 10:
        notifications.append({
            "type": "info",
            "icon": "⏰",
            "message": f"Class ending in {minutes_remaining} minutes",
            "time": current_time.strftime("%H:%M")
        })
    
    # Comfort alerts
    if comfort < 50:
        notifications.append({
            "type": "warning",
            "icon": "😰",
            "message": "Poor comfort conditions - Action needed",
            "time": current_time.strftime("%H:%M")
        })
    
    # Air quality alerts
    if co2 > 1000:
        notifications.append({
            "type": "alert",
            "icon": "🌬️",
            "message": "High CO2 detected - Open windows immediately",
            "time": current_time.strftime("%H:%M")
        })
    
    # Temperature alerts
    if temperature > 30:
        notifications.append({
            "type": "alert",
            "icon": "🔥",
            "message": "High temperature - AC activation recommended",
            "time": current_time.strftime("%H:%M")
        })
    
    # Occupancy alerts
    if people_count > 45:
        notifications.append({
            "type": "warning",
            "icon": "👥",
            "message": "Near capacity - Monitor for overcrowding",
            "time": current_time.strftime("%H:%M")
        })
    
    # Anomaly notifications
    for anomaly in anomalies:
        notifications.append({
            "type": "critical",
            "icon": "🚨",
            "message": anomaly,
            "time": current_time.strftime("%H:%M")
        })
    
    return notifications[-5:]  # Return last 5 notifications


def calculate_occupancy_trend():
    """
    Calculate if occupancy is increasing, decreasing, or stable
    """
    if len(occupancy_history) < 3:
        return "Stable", 0
    
    recent = list(occupancy_history)[-3:]
    
    if recent[-1] > recent[0] + 5:
        change = recent[-1] - recent[0]
        return "Increasing", change
    elif recent[-1] < recent[0] - 5:
        change = recent[0] - recent[-1]
        return "Decreasing", -change
    else:
        return "Stable", 0


def get_course_code(slot_code):
    """
    Convert slot code to course code using OCR-extracted data
    """
    # First try OCR-extracted mappings
    try:
        with open("course_mapping_extracted.json", "r") as f:
            extracted_mapping = json.load(f)
        
        if slot_code in extracted_mapping:
            return extracted_mapping[slot_code]
    except FileNotFoundError:
        pass
    
    # Handle embedded course codes in slot names
    if "+" in slot_code:
        parts = slot_code.split("+")
        for part in parts:
            if "-" in part:
                course = part.split("-")[1]
                if re.match(r'^[A-Z]{3}\d{4}$', course):
                    return course
    
    if "-" in slot_code:
        parts = slot_code.split("-")
        if len(parts) > 1:
            course = parts[1].split("+")[0]
            if re.match(r'^[A-Z]{3}\d{4}$', course):
                return course
    
    # Return slot code if no mapping found
    return slot_code


def get_next_class_info():
    """
    Intelligent next class prediction with next-day awareness
    If no more classes today, automatically looks for tomorrow's first class
    """
    try:
        with open("timetable_map.json", "r") as f:
            timetable_map = json.load(f)
    except FileNotFoundError:
        return "No timetable", "N/A", "N/A", 0
    except json.JSONDecodeError:
        print("❌ Error: timetable_map.json is corrupted or empty")
        return "No timetable", "N/A", "N/A", 0
    
    now = datetime.now()
    current_time = now.time()
    current_day = now.strftime("%a").upper()[:3]
    
    # Day order for next-day prediction
    day_order = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    
    if current_day not in day_order:
        return "No more classes", "N/A", "N/A", 0
    
    current_day_index = day_order.index(current_day)
    
    # First, try to find next class today
    if current_day in timetable_map:
        today_classes = timetable_map[current_day]
        
        for cls in today_classes:
            class_start_time = datetime.strptime(cls["start"], "%H:%M").time()
            if current_time < class_start_time:
                class_datetime = datetime.combine(now.date(), class_start_time)
                minutes_until = int((class_datetime - now).total_seconds() / 60)
                
                course_code = cls.get("course", "Unknown")
                class_type = cls.get("type", "Unknown")
                venue = cls.get("venue", "-")
                
                return course_code, class_type, cls["start"], minutes_until
    
    # No more classes today - look for tomorrow's first class
    print("🔮 No more classes today, checking tomorrow...")
    print(f"   Current day: {current_day} (index {current_day_index})")
    
    for i in range(1, 8):  # Check next 7 days
        next_day_index = (current_day_index + i) % 7
        next_day = day_order[next_day_index]
        
        print(f"   Checking {next_day}... ", end="")
        
        if next_day in timetable_map and timetable_map[next_day]:
            print(f"Found {len(timetable_map[next_day])} classes")
            
            # Get first class of next day
            first_class = timetable_map[next_day][0]
            
            # Calculate time until next day's class
            days_ahead = i
            next_date = now.date() + timedelta(days=days_ahead)
            class_start_time = datetime.strptime(first_class["start"], "%H:%M").time()
            class_datetime = datetime.combine(next_date, class_start_time)
            
            minutes_until = int((class_datetime - now).total_seconds() / 60)
            hours_until = minutes_until // 60
            
            course_code = first_class.get("course", "Unknown")
            class_type = first_class.get("type", "Unknown")
            venue = first_class.get("venue", "-")
            
            print(f"✅ Next class: {course_code} on {next_day} at {first_class['start']} ({hours_until}h {minutes_until % 60}m away)")
            
            return f"{course_code} ({next_day})", class_type, first_class["start"], minutes_until
        else:
            print("No classes")
    
    return "No more classes", "N/A", "N/A", 0
    """
    AI-powered energy prediction in kWh
    """
    base_consumption = 0.5  # Base load
    
    # Lighting
    if actions["lights"] == "ON":
        base_consumption += 0.3 * (people_count / 50)
    
    # Fan consumption
    fan_power = {"OFF": 0, "LOW": 0.075, "MEDIUM": 0.15, "HIGH": 0.25}
    base_consumption += fan_power.get(actions["fan"], 0)
    
    # AC consumption (highest)
    if "ON" in actions["ac"]:
        base_consumption += 2.5 + (temperature - 22) * 0.1
    
    return round(base_consumption, 2)


def predict_optimal_temperature(people_count, current_temp):
    """
    AI predicts optimal temperature based on occupancy
    """
    # More people = need cooler temp
    optimal = 24 - (people_count / 100)
    
    # Predict time to reach optimal
    temp_diff = abs(current_temp - optimal)
    time_to_optimal = int(temp_diff * 2)  # ~2 min per degree
    
    return round(optimal, 1), time_to_optimal


def detect_anomalies(people_count, temperature, noise, co2):
    """
    AI anomaly detection for security and safety
    """
    anomalies = []
    current_hour = datetime.now().hour
    
    # After hours activity
    if (current_hour < 7 or current_hour > 20) and people_count > 0:
        anomalies.append("⚠️ After-hours activity detected")
    
    # Extreme temperature
    if temperature > 35:
        anomalies.append("🔥 Critical temperature - Fire risk")
    elif temperature < 15:
        anomalies.append("❄️ Abnormally cold - HVAC failure")
    
    # Extreme noise
    if noise > 85:
        anomalies.append("🚨 Excessive noise - Possible emergency")
    
    # CO2 levels (air quality)
    if co2 > 1500:
        anomalies.append("☣️ Dangerous CO2 levels - Ventilation required")
    elif co2 > 1000:
        anomalies.append("⚠️ High CO2 - Poor air quality")
    
    # Overcrowding safety
    if people_count > 50:
        anomalies.append("⛔ Fire safety limit exceeded")
    
    # Empty class during scheduled time
    if 9 <= current_hour <= 17 and people_count == 0:
        anomalies.append("📭 Scheduled class - No attendance")
    
    return anomalies


def ai_recommendations(people_count, temperature, noise, comfort, co2):
    """
    AI-powered smart recommendations
    """
    recommendations = []
    
    # Comfort optimization
    if comfort < 60:
        if temperature > 28:
            recommendations.append("💡 Activate AC to improve comfort")
        if noise > 60:
            recommendations.append("🔇 High noise detected - Consider break time")
        if co2 > 1000:
            recommendations.append("🪟 Open windows - Poor air quality")
    
    # Energy optimization
    if people_count < 5 and temperature < 26:
        recommendations.append("⚡ Low occupancy - Switch to energy-saving mode")
    
    # Productivity optimization
    if noise > 65:
        recommendations.append("📢 Noise affecting learning - Reduce distractions")
    
    if temperature > 27 and people_count > 30:
        recommendations.append("🌡️ Pre-cool classroom before next session")
    
    # Health & wellness
    if people_count > 35:
        recommendations.append("🪟 High occupancy - Increase ventilation")
    
    if co2 > 800:
        recommendations.append("🌬️ CO2 levels rising - Improve air circulation")
    
    return recommendations


def smart_automation(people_count, temperature, noise):
    """
    AI-Powered Intelligent Automation with Predictive Control
    """
    actions = {
        "lights": "OFF",
        "fan": "OFF",
        "ac": "OFF",
        "mode": "Idle",
        "energy_kwh": 0,
        "optimal_temp": 24,
        "time_to_optimal": 0,
        "anomalies": [],
        "recommendations": []
    }
    
    # No one in classroom
    if people_count == 0:
        actions["mode"] = "🌙 Idle - Energy Saving"
        actions["energy_kwh"] = predict_energy_consumption(people_count, temperature, actions)
        return actions
    
    # People detected - activate systems
    actions["lights"] = "ON"
    actions["mode"] = "🟢 Active"
    
    # Predictive temperature control
    optimal_temp, time_to_optimal = predict_optimal_temperature(people_count, temperature)
    actions["optimal_temp"] = optimal_temp
    actions["time_to_optimal"] = time_to_optimal
    
    # Smart temperature-based cooling with prediction
    if temperature < 24:
        actions["fan"] = "OFF"
        actions["ac"] = "OFF"
        actions["mode"] = "🟢 Active - Optimal Comfort"
    elif 24 <= temperature < 27:
        actions["fan"] = "LOW"
        actions["ac"] = "OFF"
        actions["mode"] = "🟢 Active - Comfortable"
    elif 27 <= temperature < 29:
        actions["fan"] = "MEDIUM"
        actions["ac"] = "OFF"
        actions["mode"] = "🟡 Active - Moderate Cooling"
    elif 29 <= temperature < 31:
        actions["fan"] = "HIGH"
        actions["ac"] = "ON (24°C)"
        actions["mode"] = "🟠 Active - High Cooling"
    else:  # >= 31
        actions["fan"] = "HIGH"
        actions["ac"] = "ON (22°C)"
        actions["mode"] = "🔴 Active - Maximum Cooling"
    
    # Noise-based intelligent alerts
    if noise > 70:
        actions["mode"] = "🔴 Active - High Noise Alert"
    elif noise > 55:
        actions["mode"] = "🟡 Active - Moderate Noise"
    
    # Overcrowding alert
    if people_count > 40:
        actions["mode"] = "⚠️ Active - Overcrowded"
    
    # Calculate energy consumption
    actions["energy_kwh"] = predict_energy_consumption(people_count, temperature, actions)
    
    return actions


def realtime_loop():
    """
    AI-Powered Real-Time Monitoring with Advanced Analytics
    """
    global peak_occupancy_today, total_energy_consumed, total_people_minutes, class_sessions_today
    
    iteration_count = 0
    
    while True:
        people_count = state["people"]
        
        # Simulate environmental sensors (replace with real IoT sensors)
        temperature, noise, co2, humidity, air_quality = simulate_environmental_data(people_count)
        
        # Update environmental context
        state["context"]["temperature"] = temperature
        state["context"]["noise"] = noise
        state["context"]["co2"] = co2
        state["context"]["humidity"] = humidity
        state["context"]["air_quality"] = air_quality
        
        # Calculate comfort score
        comfort = calculate_comfort(temperature, noise, people_count, co2, humidity)
        state["comfort"] = comfort
        
        # Calculate productivity score
        productivity = calculate_productivity_score(comfort, noise, co2, temperature)
        
        # Detect attention patterns
        attention_status = detect_attention_patterns(people_count, noise)
        
        # Attendance is now managed by camera module with face recognition
        # No need to generate generic attendance here anymore
        if "attendance" not in state or not state["attendance"]:
            # Fallback: Generate generic attendance if face recognition is disabled
            state["attendance"] = [
                {"id": f"Student_{i+1:03d}", "name": f"Student_{i+1:03d}", "confidence": 1.0}
                for i in range(people_count)
            ]
        
        # Apply AI-powered smart automation
        actions = smart_automation(people_count, temperature, noise)
        state["actions"] = actions
        
        # Calculate energy consumption
        energy_kwh = predict_energy_consumption(people_count, temperature, actions)
        state["actions"]["energy_kwh"] = energy_kwh
        
        # Track total energy
        total_energy_consumed += energy_kwh * (3 / 3600)  # Convert to 3-second intervals
        
        # Calculate energy cost
        energy_cost = total_energy_consumed * ENERGY_COST_PER_KWH
        
        # Calculate carbon footprint
        co2_emissions, trees_needed = calculate_carbon_footprint(total_energy_consumed)
        
        # Calculate energy savings
        energy_saved, savings_percentage = calculate_energy_savings()
        
        # AI Anomaly Detection
        anomalies = detect_anomalies(people_count, temperature, noise, co2)
        state["anomalies"] = anomalies
        
        # AI Recommendations
        recommendations = ai_recommendations(people_count, temperature, noise, comfort, co2)
        state["recommendations"] = recommendations
        
        # Generate smart notifications
        notifications = generate_smart_notifications(people_count, comfort, co2, temperature, anomalies)
        state["notifications"] = notifications
        
        # Track peak occupancy
        if people_count > peak_occupancy_today:
            peak_occupancy_today = people_count
        
        # Track people-minutes for average calculation
        total_people_minutes += people_count * (3 / 60)  # 3-second intervals
        
        # Calculate occupancy trend
        occupancy_trend, trend_change = calculate_occupancy_trend()
        
        # Predict next hour occupancy
        predicted_occupancy = predict_next_hour_occupancy()
        
        # Get next class info
        next_subject, next_type, next_time, minutes_until = get_next_class_info()
        
        # Class end prediction
        class_end_time, minutes_to_end = predict_class_end_time()
        
        # Update statistics
        uptime_hours = (datetime.now() - SYSTEM_START_TIME).total_seconds() / 3600
        avg_occupancy = int(total_people_minutes / max(uptime_hours, 0.01))
        
        state["statistics"] = {
            "total_classes_today": class_sessions_today,
            "avg_occupancy": avg_occupancy,
            "peak_occupancy": peak_occupancy_today,
            "total_energy_today": round(total_energy_consumed, 2),
            "energy_cost_today": round(energy_cost, 2),
            "uptime_hours": round(uptime_hours, 2),
            "productivity_score": productivity,
            "attention_status": attention_status,
            "occupancy_trend": occupancy_trend,
            "trend_change": trend_change,
            "predicted_next_hour": predicted_occupancy,
            "energy_saved": energy_saved,
            "savings_percentage": savings_percentage,
            "co2_emissions_kg": co2_emissions,
            "trees_equivalent": trees_needed,
            "next_class_subject": next_subject,
            "next_class_type": next_type,
            "next_class_time": next_time,
            "minutes_until_next": minutes_until,
            "class_end_time": class_end_time,
            "minutes_to_end": minutes_to_end
        }
        
        # Store history every 5 minutes (100 iterations at 3 seconds each)
        iteration_count += 1
        if iteration_count % 100 == 0:
            occupancy_history.append(people_count)
            energy_history.append(energy_kwh)
            comfort_history.append(comfort)
        
        # Enhanced console output
        print(f"\n{'='*70}")
        print(f"🤖 AI SMART CLASSROOM SYSTEM - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}")
        print(f"👥 Occupancy: {people_count} students | Trend: {occupancy_trend} ({trend_change:+d})")
        print(f"🌡️  Temperature: {temperature}°C | Optimal: {actions.get('optimal_temp', 24)}°C")
        print(f"🔊 Noise: {noise} dB | 🌬️  CO2: {co2} ppm ({air_quality})")
        print(f"💧 Humidity: {humidity}% | 😊 Comfort: {comfort}%")
        print(f"🎯 Productivity: {productivity}% | {attention_status}")
        print(f"⚡ Energy: {energy_kwh} kWh | Cost: ₹{energy_cost:.2f}")
        print(f"🌱 CO2: {co2_emissions} kg | Trees: {trees_needed}")
        print(f"💰 Saved: {energy_saved} kWh ({savings_percentage}%)")
        print(f"🎯 Mode: {actions.get('mode', 'Unknown')}")
        
        if minutes_to_end > 0:
            print(f"⏰ Class ends in {minutes_to_end} minutes")
        
        if minutes_until > 0 and minutes_until < 60:
            print(f"📚 Next: {next_subject} in {minutes_until} minutes")
        
        if anomalies:
            print(f"\n⚠️  ANOMALIES:")
            for anomaly in anomalies:
                print(f"   {anomaly}")
        
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"   {rec}")
        
        print(f"{'='*70}\n")
        
        time.sleep(3)
