import tkinter as tk
from tkinter import ttk
import pymongo
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import json
import pytz

import settings

mongo_client = MongoClient(settings.MONGO_URI)
db = mongo_client[settings.MONGO_DATABASE]

window = tk.Tk()
window.title("Smart Home Dashboard")
window.geometry("800x600")

main_frame = ttk.Frame(window, padding="20")
main_frame.pack(fill="both", expand=True)

sensor_frames = {}
for sensor in settings.MONGO_COLLECTIONS.keys():
    sensor_frame = ttk.Frame(main_frame, padding="10")
    sensor_frame.pack(fill="x", padx=10, pady=5)
    sensor_frames[sensor] = sensor_frame

labels = {}
timestamps = {}
for sensor, frame in sensor_frames.items():
    label = ttk.Label(frame, font=("Arial", 12))
    label.pack(fill="both", expand=True)
    labels[sensor] = label
    timestamps[sensor] = None

warning_frame = ttk.Frame(main_frame, padding="10")
warning_frame.pack(fill="x", padx=10, pady=5)

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
    sensor_data = {}

    for sensor, sensor_settings in settings.MONGO_COLLECTIONS.items():
        collection = db[sensor_settings['collection']]
        latest_data = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
        sensor_data[sensor] = latest_data

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


def on_connect(mqtt_client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    mqtt_client.subscribe([(settings.MONGO_COLLECTIONS[sensor]['topic'], 0) for sensor in settings.MONGO_COLLECTIONS])
    mqtt_client.subscribe(settings.TOPIC_WARNING_ALARM)


def on_message(mqtt_client, userdata, msg):
    print(f"Message received on topic {msg.topic} with payload {msg.payload}")

    sensor_name = msg.topic.rsplit('/', 1)[-1]

    label = labels.get(sensor_name)
    if label:
        data = json.loads(msg.payload.decode("utf-8"))
        text = f"{settings.MONGO_COLLECTIONS[sensor_name]['name']}:\n"

        for key, value in data.items():
            text += f"{settings.gui_labels.get(key, key.capitalize())}: {value}\n"

        label.configure(text=text)

        if msg.topic == settings.TOPIC_WARNING_ALARM:
            print('Warning message received')
            warning_message = json.loads(msg.payload.decode("utf-8"))
            handle_warning_message(warning_message)
        else:
            warning_label = warning_labels.get(msg.topic)
            if warning_label:
                warning_label.configure(text="")

    if msg.topic == settings.TOPIC_WARNING_ALARM:
        print('Warning message received')
        warning_message = json.loads(msg.payload.decode("utf-8"))
        handle_warning_message(warning_message)


def handle_warning_message(warning_message):
    print('here')
    message = warning_message.get("message")
    topic = warning_message.get("topic")

    warning_label = warning_labels.get(topic)
    if warning_label:
        warning_label.configure(text=message)

    print(f"Received Warning Message: {message} (Topic: {topic})")


def run_gui():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
    mqtt_client.loop_start()

    update_labels()

    try:
        window.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run_gui()
