import time
import random
import requests

API = "http://127.0.0.1:5001/api/sensors"

DEVICES = ["device-1", "device-2", "device-3"]
SENSOR_TYPES = [
    ("temperature", "C", 20, 75),
    ("humidity", "%", 30, 95),
    ("vibration", "g", 0.0, 6.0)
]

def simulate_one():
    device = random.choice(DEVICES)
    s_type, unit, base, upper = random.choice(SENSOR_TYPES)
    value = round(random.uniform(base, upper), 2)
    payload = {
        "device_id": device,
        "sensor_type": s_type,
        "value": value,
        "unit": unit
    }
    try:
        r = requests.post(API, json=payload, timeout=2)
        print(r.status_code, r.json())
    except Exception as e:
        print("Failed to post:", e)

if __name__ == "__main__":
    while True:
        simulate_one()
        time.sleep(2)
