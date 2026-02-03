# AHT10 Linux IOT Gateway 🌡️📡

A professional-grade IoT Edge Gateway solution for local climate monitoring. This project demonstrates the integration of Linux kernel industrial I/O (IIO) drivers, MQTT messaging, and automated system services on a Raspberry Pi.

## 🚀 Overview
This project transforms a Raspberry Pi into an autonomous IoT hub that:
- **Acquires Data**: Reads Temperature and Humidity from an AHT10 sensor via the Linux `/sys/class/hwmon` interface.
- **Optimizes Telemetry**: Implements "Report-by-Exception" logic (Deadband filtering) to only transmit data when significant changes occur.
- **Ensures Reliability**: Features a local CSV logging system for data persistence during network outages.
- **Supervises**: Hosts a local Mosquitto MQTT broker and a Node-RED dashboard for real-time visualization.

## 🛠️ Tech Stack
- **Hardware**: Raspberry Pi (any model with I2C), AHT10 Sensor.
- **Language**: Python 3.
- **Protocol**: MQTT (Mosquitto).
- **Dashboard**: Node-RED.
- **OS Integration**: Systemd (Linux Service), Bash (Automation).

## 📂 Project Structure
```text
├── src/
│   ├── aht10_collector.py   # Main logic: Sensor reading & MQTT publishing
│   └── logger.py            # Backup utility: Local CSV data logging
├── config/
│   ├── mosquitto.conf       # Optimized MQTT Broker configuration
│   └── node_red_flow.json   # Exported dashboard for rapid deployment
├── systemd/
│   └── iot_gateway.service  # Linux service for 24/7 background operation
├── setup.sh                 # One-click installation script
└── requirements.txt         # Python dependencies
```


## ⚙️ Installation & Setup Guide
**1. Hardware Connection:**
Connect the AHT10 sensor to the Raspberry Pi GPIO pins as follows:
```text
AHT10 Pin|RPi Pin (Physical)|Function
VCC      |Pin 1             |3.3V Power
GND      |Pin 9             |Ground
SDA      |Pin 3             |I2C Data (GPIO 2)
SCL      |Pin 5             |I2C Clock (GPIO 3)
```

**2. Prepare the Operating System**
The Linux kernel must have I2C enabled to expose the sensor to the `/sys/class/hwmon` interface:
1. Open the terminal and run: `sudo raspi-config`
2. Navigate to Interface Options -> I2C.
3. Select Yes to enable it.
4. Reboot your Raspberry Pi.

**3. Automated Deployment**
This project includes a setup.sh script that automates the environment setup, including dependency installation and the creation of the system service.
```Bash
 Clone the repository
git clone [https://github.com/yourusername/AHT10-Linux-IIO-Gateway.git](https://github.com/yourusername/AHT10-Linux-IIO-Gateway.git)
cd AHT10-Linux-IIO-Gateway
# Make the script executable and run it
chmod +x setup.sh
./setup.sh
```
**4. Setting up the Dashboard**
To visualize your telemetry data:
1. Open Node-RED (usually at http://<your-pi-ip>:1880).
2. Click the Menu (top right) -> Import.
3. Paste the contents of config/node_red_flow.json or upload the file.
4. Click Deploy.
5. Access the live UI at http://<your-pi-ip>:1880/ui.
## 🛠️ Management & Monitoring
The gateway runs automatically in the background as a **Systemd Service**. You can manage it with these commands:
- Check Status: `systemctl status iot_gateway.service`
- View Real-time Logs: `journalctl -u iot_gateway.service -f`
- Stop Service: `sudo systemctl stop iot_gateway.service`
- Restart Service: `sudo systemctl restart iot_gateway.service`

  ## 🧠 Key Logic: Report-by-Exception
  To optimize network bandwidth and storage, the system only logs and publishes data if:
  1. It is the first reading after startup.
  2. Temperature changes by more than 0.5°C.
  3. Humidity changes by more than 1.0%.
