import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

# Sample data for three systems
systems = {
    "System 1": [
        {"student_id": "S001", "start": "8:00", "stop": "9:00"},
        {"student_id": "S002", "start": "8:30", "stop": "9:30"},
        {"student_id": "S003", "start": "9:00", "stop": "10:00"},
    ],
    "System 2": [
        {"student_id": "S001", "start": "8:15", "stop": "9:15"},
        {"student_id": "S002", "start": "8:45", "stop": "9:45"},
        {"student_id": "S004", "start": "9:30", "stop": "10:30"},
    ],
    "System 3": [
        {"student_id": "S003", "start": "8:20", "stop": "9:20"},
        {"student_id": "S004", "start": "8:40", "stop": "9:40"},
        {"student_id": "S005", "start": "9:15", "stop": "10:15"},
    ]
}

# Function to convert time strings to datetime objects
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# Create plot data
plot_data = {}
for system, accesses in systems.items():
    plot_data[system] = []
    for access in accesses:
        start_time = parse_time(access["start"])
        end_time = parse_time(access["stop"])
        plot_data[system].append((start_time, end_time))

# Function to plot the data
def plot_access_times(plot_data):
    plt.figure(figsize=(10, 6))
    for system, accesses in plot_data.items():
        for access in accesses:
            plt.barh(system, left=access[0], width=access[1]-access[0], height=0.5, align='center')
    plt.xlabel('Time')
    plt.ylabel('System Name')
    plt.title('System Access Times')
    plt.tight_layout()
    plt.show()

# Plot the data
plot_access_times(plot_data)
