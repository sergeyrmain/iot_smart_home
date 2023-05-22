import threading
import paho.mqtt.client as mqtt
import random
import time
import json

import settings

mqttBroker = settings.MQTT_BROKER


# temperature and humidity emulator
#  simulates a temperature and humidity sensor
# this sensor would measure the temperature and humidity in its environment and send these reading
def temperature_humidity_emulator():
    client = mqtt.Client("Temperature_Humidity_Emulator")
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)

    while True:
        temp = round(random.uniform(*settings.TEMP_RANGE), 2)
        humidity = round(random.uniform(*settings.HUMIDITY_RANGE), 2)
        message = {"temperature": temp, "humidity": humidity}
        message = json.dumps(message)

        client.publish(settings.TOPIC_TEMPERATURE_HUMIDITY, message)
        print(f"Just published {message} to Topic {settings.TOPIC_TEMPERATURE_HUMIDITY}")
        time.sleep(15)


# button emulator
#  which is a simple digital input device that can be either ON or OFF
def button_emulator():
    client = mqtt.Client("Button_Emulator")
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)

    button_state = False

    while True:
        button_state = not button_state
        payload = json.dumps({"button_state": button_state})  # Convert button state to JSON payload

        client.publish(settings.TOPIC_BUTTON, payload)
        print(f"Just published {payload} to Topic {settings.TOPIC_BUTTON}")
        time.sleep(15)


# light sensor emulator
# measures the intensity of light.

def light_sensor_emulator():
    client = mqtt.Client("LightSensor_Emulator")
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)

    while True:
        light_intensity = round(random.uniform(*settings.LIGHT_INTENSITY_RANGE), 2)
        message = {"intensity": light_intensity}
        message = json.dumps(message)
        client.publish(settings.TOPIC_LIGHT_SENSOR, message)
        print(f"Just published {message} to Topic {settings.TOPIC_LIGHT_SENSOR}")
        time.sleep(15)


def conditioner_emulator():
    client = mqtt.Client("Conditioner_Emulator")
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)

    while True:
        temperature = round(random.uniform(*settings.TEMP_RANGE), 2)

        if temperature > settings.TEMPERATURE_THRESHOLD_HOT:
            status = "Cooling"
        elif temperature < settings.TEMPERATURE_THRESHOLD_COLD:
            status = "Heating"
        else:
            status = "Idle"

        message = {"temperature": temperature, "status": status}
        message = json.dumps(message)

        client.publish(settings.TOPIC_CONDITIONER, message)
        print(f"Just published {message} to Topic {settings.TOPIC_CONDITIONER}")

        time.sleep(15)


def run_emulators():
    print("Starting temperature_humidity_emulator")
    threading.Thread(target=temperature_humidity_emulator).start()
    time.sleep(3)
    print("Starting button_emulator")
    threading.Thread(target=button_emulator).start()
    time.sleep(3)
    print("Starting light_sensor_emulator")
    threading.Thread(target=light_sensor_emulator).start()
    time.sleep(3)
    print("Starting conditioner_emulator")
    threading.Thread(target=conditioner_emulator).start()


if __name__ == '__main__':
    run_emulators()
