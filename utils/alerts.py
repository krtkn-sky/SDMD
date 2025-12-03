# simple rule engine for alerts
THRESHOLDS = {
    # sensor_type: (low_threshold, high_threshold)
    "temperature": (None, 60),  # degrees C
    "humidity": (None, 90),     # percent
    "vibration": (None, 5.0)    # arbitrary units
}

def check_alerts(device_id, sensor_type, value):
    """
    Return None if no alert, else a dict with alert info.
    """
    th = THRESHOLDS.get(sensor_type)
    if not th:
        return None
    low, high = th
    if high is not None and value > high:
        return {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "severity": "HIGH",
            "message": f"{sensor_type} reading {value} exceeds threshold {high}"
        }
    if low is not None and value < low:
        return {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "severity": "HIGH",
            "message": f"{sensor_type} reading {value} below threshold {low}"
        }
    return None
