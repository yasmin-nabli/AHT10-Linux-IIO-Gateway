import csv
import os
from datetime import datetime

class DataLogger:
    def __init__(self, filename="sensor_backup.csv"):
        self.filename = filename
        # Create file with header if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Temperature_C", "Humidity_Pct"])

    def log_data(self, temp, hum):
        """Appends a new row of data to the CSV file."""
        try:
            with open(self.filename, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), temp, hum])
        except Exception as e:
            print(f"Backup Error: {e}")