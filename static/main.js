async function fetchLatest() {
  try {
    const res = await fetch('/api/sensors/latest_by_device');
    const data = await res.json();
    const tbody = document.getElementById('readings-body');
    tbody.innerHTML = '';
    const alertsDiv = document.getElementById('alerts');
    alertsDiv.innerHTML = '';

    data.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${row.device_id}</td>
        <td>${row.sensor_type}</td>
        <td>${row.value}</td>
        <td>${row.unit}</td>
        <td>${row.timestamp}</td>
      `;
      tbody.appendChild(tr);

      // quick client-side alert highlight (also server returns alerts on POST)
      // simple rule: if value seems out of human bounds, show it
      if ((row.sensor_type === 'temperature' && row.value > 60) ||
          (row.sensor_type === 'humidity' && row.value > 90) ||
          (row.sensor_type === 'vibration' && row.value > 5.0)) {
        const warn = document.createElement('div');
        warn.className = 'alert alert-danger';
        warn.textContent = `ALERT: ${row.device_id} ${row.sensor_type} = ${row.value} ${row.unit}`;
        alertsDiv.appendChild(warn);
      }
    });
  } catch (e) {
    console.error(e);
  }
}

document.getElementById('refresh').addEventListener('click', fetchLatest);
setInterval(fetchLatest, 5000); // auto-refresh every 5s
fetchLatest();
