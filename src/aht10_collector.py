import time
import os
import paho.mqtt.client as mqtt
from logger import DataLogger

class AHT10Collector:
    def __init__(self, broker="localhost", port=1883):
        self.client_id = "csf_pub"
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(self.client_id)
        self.backup = DataLogger("sensor_backup.csv")
        
        # Thresholds (Change detection)
        self.TEMP_THRESHOLD = 0.5   # Send if temp changes by 0.5°C
        self.HUM_THRESHOLD = 1.0    # Send if hum changes by 1%
        
        # Memory of last sent values
        self.last_temp = None
        self.last_hum = None
        # Topics
        self.topic_temp = "sensor/temperature"
        self.topic_hum = "sensor/humidity"

        # Path discovery (Finds where the AHT10 is mapped)
        self.base_path = self._find_hwmon_path("aht10") 

    def _find_hwmon_path(self, sensor_name):
        """Automatically finds the hwmon directory for a specific sensor name."""
        for root, dirs, files in os.walk('/sys/class/hwmon/'):
            try:
                with open(os.path.join(root, 'name'), 'r') as f:
                    if sensor_name in f.read():
                        return root
            except (FileNotFoundError, PermissionError):
                continue
        # Fallback to your specific path if discovery fails
        return '/sys/class/hwmon/hwmon2'

    def read_sysfs(self, filename):
        """Reads values from the Linux Sysfs files."""
        try:
            path = os.path.join(self.base_path, filename)
            with open(path, 'r') as file:
                return int(file.read().strip())
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}")

        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)

    def run(self):
        self.connect_mqtt()
        self.client.loop_start()
        print("Collector Started: Reporting by Exception (Change Detection)...")

        try:
            while True:
                raw_temp = self.read_sysfs('temp1_input')
                raw_hum = self.read_sysfs('humidity1_input')
                
                if raw_temp is not None and raw_hum is not None:
                    curr_temp = round(raw_temp / 1000.0, 2)
                    curr_hum = round(raw_hum / 1000.0 if raw_hum > 1000 else raw_hum, 2)

                    # Logic: Is this the first run OR has a value changed significantly?
                    is_first_run = self.last_temp is None or self.last_hum is None
                    temp_changed = not is_first_run and abs(curr_temp - self.last_temp) >= self.TEMP_THRESHOLD
                    hum_changed = not is_first_run and abs(curr_hum - self.last_hum) >= self.HUM_THRESHOLD

                    if is_first_run or temp_changed or hum_changed:
                        # 1. Update memory
                        self.last_temp = curr_temp
                        self.last_hum = curr_hum

                        # 2. Publish to MQTT (Both values sent as per your requirement)
                        self.client.publish(self.topic_temp, curr_temp)
                        self.client.publish(self.topic_hum, curr_hum)
                        
                        # 3. Save to Logger
                        self.backup.log_data(curr_temp, curr_hum)
                        
                        print(f"[SEND] Change detected! Temp: {curr_temp}C, Hum: {curr_hum}%")
                    else:
                        print(f"[IDLE] No significant change. T:{curr_temp} H:{curr_hum}")

                # Check sensor every 5 seconds, but only send on change
                time.sleep(5)
        except KeyboardInterrupt:
            self.client.disconnect()
        self.connect_mqtt()
        self.client.loop_start()
        print(f"Monitoring AHT10 at {self.base_path}...")

        try:
            while True:
                # Temperature processing
                raw_temp = self.read_sysfs('temp1_input')
                if raw_temp is not None:
                    temp_c = raw_temp / 1000.0
                    self.client.publish(self.topic_temp, f"{temp_c:.2f}")
                    print(f"Published Temp: {temp_c}°C")

                # Humidity processing
                raw_hum = self.read_sysfs('humidity1_input')
                if raw_hum is not None:
                    # Note: Some drivers provide millipercent, some provide 0-100
                    hum_pct = raw_hum / 1000.0 if raw_hum > 1000 else raw_hum
                    self.client.publish(self.topic_hum, f"{hum_pct:.2f}")
                    print(f"Published Humidity: {hum_pct}%")
                
                self.backup.log_data(temp_c, hum_pct)

                time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping...")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    collector = AHT10Collector()
    collector.run()