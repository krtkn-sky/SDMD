import sqlite3
from flask import Flask, g, request, jsonify, render_template
from flask_cors import CORS
from utils.alerts import check_alerts

DATABASE = 'database.db'
APP = Flask(__name__)
CORS(APP)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            sensor_type TEXT,
            value REAL,
            unit TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    db.commit()

@APP.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@APP.route('/')
def index():
    return render_template('dashboard.html')

@APP.route('/api/sensors', methods=['POST'])
def receive_sensor():
    """
    Expected JSON:
    {
      "device_id": "device-1",
      "sensor_type": "temperature",
      "value": 34.5,
      "unit": "C"
    }
    """
    payload = request.get_json()
    device_id = payload.get('device_id')
    sensor_type = payload.get('sensor_type')
    value = payload.get('value')
    unit = payload.get('unit', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO sensors (device_id, sensor_type, value, unit) VALUES (?, ?, ?, ?)',
        (device_id, sensor_type, value, unit)
    )
    db.commit()

    alert = check_alerts(device_id, sensor_type, value)
    return jsonify({"status": "ok", "alert": alert}), 201

@APP.route('/api/sensors/recent', methods=['GET'])
def recent_sensors():
    """
    Query params:
      ?limit=50
    """
    limit = int(request.args.get('limit', 50))
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sensors ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    data = [dict(r) for r in rows]
    return jsonify(data)

@APP.route('/api/sensors/latest_by_device', methods=['GET'])
def latest_by_device():
    db = get_db()
    cursor = db.cursor()
    # returns last reading per device+sensor_type
    cursor.execute('''
        SELECT s1.* FROM sensors s1
        JOIN (
            SELECT device_id, sensor_type, MAX(timestamp) AS maxt FROM sensors GROUP BY device_id, sensor_type
        ) s2 ON s1.device_id = s2.device_id AND s1.sensor_type = s2.sensor_type AND s1.timestamp = s2.maxt
    ''')
    rows = cursor.fetchall()
    data = [dict(r) for r in rows]
    return jsonify(data)

if __name__ == '__main__':
    with APP.app_context():
        init_db()
    APP.run(host='0.0.0.0', port=5001, debug=True)
