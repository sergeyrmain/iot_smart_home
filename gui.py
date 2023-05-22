import tkinter as tk
from tkinter import ttk
import pymongo
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import json
import pytz
from datetime import datetime, timedelta

# Import settings
import settings

# MongoDB connection
mongo_client = MongoClient(settings.MONGO_URI)
db = mongo_client[settings.MONGO_DATABASE]

# Create a new tkinter window
window = tk.Tk()
window.title("Smart Home Dashboard")
window.geometry("800x600")  # Set the window size to 800x600

# Create a frame for the main content
main_frame = ttk.Frame(window, padding="20")
main_frame.pack(fill="both", expand=True)

# Create a frame for each sensor reading
sensor_frames = {}
for sensor in settings.MONGO_COLLECTIONS.keys():
    sensor_frame = ttk.Frame(main_frame, padding="10")
    sensor_frame.pack(fill="x", padx=10, pady=5)
    sensor_frames[sensor] = sensor_frame

# Create labels for temperature, humidity, light level, and button state
labels = {}
timestamps = {}
for sensor, frame in sensor_frames.items():
    label = ttk.Label(frame, font=("Arial", 12))
    label.pack(fill="both", expand=True)
    labels[sensor] = label
    timestamps[sensor] = None

warning_frame = ttk.Frame(main_frame, padding="10")
warning_frame.pack(fill="x", padx=10, pady=5)

# Create a dictionary to hold warning labels for each topic
warning_labels = {}
for sensor, frame in sensor_frames.items():
    topic = settings.MONGO_COLLECTIONS[sensor]['topic']
    warning_label = ttk.Label(frame, font=("Arial", 12), foreground="red")
    warning_label.pack(fill="both", expand=True)
    warning_labels[topic] = warning_label


def convert_utc_to_local(utc_time, timezone):
    local_tz = pytz.timezone(timezone)
    local_time = utc_time.astimezone(local_tz)
    return local_time


def update_labels():
    # Fetch the latest data from the corresponding collections
    sensor_data = {}

    for sensor, sensor_settings in settings.MONGO_COLLECTIONS.items():
        collection = db[sensor_settings['collection']]
        latest_data = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
        sensor_data[sensor] = latest_data

    # Update the labels with the new data and timestamps
    for sensor, label in labels.items():
        data = sensor_data.get(sensor, {})
        if data:
            keys = settings.MONGO_COLLECTIONS[sensor]['keys']
            text = f"{settings.MONGO_COLLECTIONS[sensor]['name']}:\n"

            for key, value in data.items():
                if key != '_id':
                    text += f"{settings.gui_labels.get(key, key.capitalize())}: {value}\n"

            if '_id' in data:
                utc_timestamp = data['_id'].generation_time
                israel_timezone = pytz.timezone('Israel')
                israel_time = convert_utc_to_local(utc_timestamp, 'Israel')
                last_updated = israel_time.strftime("%Y-%m-%d %H:%M:%S")
                text += f"Last Updated (Israel Time): {last_updated}"
        else:
            text = f"{settings.MONGO_COLLECTIONS[sensor]['name']}: (DISCONNECTED)"

        label.configure(text=text)

    # Schedule the next update
    window.after(120000, update_labels)  # 5 minutes



def on_message(mqtt_client, userdata, msg):
    print(f"Message received on topic {msg.topic} with payload {msg.payload}")

    # Extract the sensor name from the topic
    sensor_name = msg.topic.rsplit('/', 1)[-1]

    # Update the corresponding label in the GUI
    label = labels.get(sensor_name)
    if label:
        data = json.loads(msg.payload.decode("utf-8"))
        text = f"{settings.MONGO_COLLECTIONS[sensor_name]['name']}:\n"

        for key, value in data.items():
            text += f"{settings.gui_labels.get(key, key.capitalize())}: {value}\n"

        label.configure(text=text)

        # Check if the message is a warning/alarm message
        if msg.topic == settings.TOPIC_WARNING_ALARM:
            print('Warning message received')
            warning_message = json.loads(msg.payload.decode("utf-8"))
            handle_warning_message(warning_message)
        else:
            # Remove the warning label for the sensor if it exists
            warning_label = warning_labels.get(msg.topic)
            if warning_label:
                warning_label.configure(text="")

    # Check if the message is a warning/alarm message
    if msg.topic == settings.TOPIC_WARNING_ALARM:
        print('Warning message received')
        warning_message = json.loads(msg.payload.decode("utf-8"))
        handle_warning_message(warning_message)


def handle_warning_message(warning_message):
    print('here')
    # Extract the warning message and topic from the payload
    message = warning_message.get("message")
    topic = warning_message.get("topic")

    # Get the corresponding warning label for the topic
    warning_label = warning_labels.get(topic)
    if warning_label:
        warning_label.configure(text=message)

    print(f"Received Warning Message: {message} (Topic: {topic})")
    # Add your code here to handle the warning message


def run_gui():
    # Create an MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message

    # Connect to the MQTT broker
    mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
    mqtt_client.loop_start()

    # Subscribe to MQTT topics
    mqtt_client.subscribe([(settings.MONGO_COLLECTIONS[sensor]['topic'], 0) for sensor in settings.MONGO_COLLECTIONS])
    mqtt_client.subscribe(settings.TOPIC_WARNING_ALARM)  # Subscribe to the warning topic

    update_labels()
    # Start the tkinter event loop
    try:
        window.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run_gui()
