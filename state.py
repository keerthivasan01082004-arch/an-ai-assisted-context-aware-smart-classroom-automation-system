state = {
    "people": 0,
    "comfort": 75,
    "context": {
        "temperature": 28,
        "noise": 35,
        "co2": 400,  # ppm
        "humidity": 60,  # percentage
        "air_quality": "Good"
    },
    "actions": {
        "lights": "OFF",
        "fan": "OFF",
        "ac": "OFF",
        "mode": "Idle",
        "energy_kwh": 0,
        "optimal_temp": 24,
        "time_to_optimal": 0
    },
    "attendance": [],
    "camera_online": False,
    "anomalies": [],
    "recommendations": [],
    "statistics": {
        "total_classes_today": 0,
        "avg_occupancy": 0,
        "peak_occupancy": 0,
        "total_energy_today": 0,
        "energy_cost_today": 0,
        "uptime_hours": 0
    },
    "history": {
        "occupancy": [],
        "comfort": [],
        "energy": [],
        "timestamps": []
    },
    "notifications": []
}
