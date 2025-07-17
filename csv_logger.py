import csv
import os
from datetime import datetime

class CsvLogger:
    """
    Class that logs data to a CSV file.
    """
    def __init__(self, base_dir, prefix='tacho_test'):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        # Generate a timestamped file name to avoid collision
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.file_path = os.path.join(self.base_dir, f'{prefix}_{timestamp}.csv')
        self._init_file()

    def _init_file(self):
        with open(self.file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['pwm', 'expected_rpm', 'measured_rpm', 'result'])

    def log_row(self, pwm, expected_rpm, measured_rpm, result):
        with open(self.file_path, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([pwm, expected_rpm, measured_rpm, result])

    def get_path(self):
        return self.file_path
