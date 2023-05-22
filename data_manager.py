import json
import pymongo
import paho.mqtt.client as mqtt
import settings


def run_data_manager():
    try:
        # Connect to MongoDB
        mongo_client = pymongo.MongoClient(settings.MONGO_URI)
        db = mongo_client[settings.MONGO_DATABASE]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        exit(1)

    # MQTT Callbacks
    def on_connect(mqtt_client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        mqtt_client.subscribe([(settings.TOPIC_TEMPERATURE_HUMIDITY, 0),
                               (settings.TOPIC_BUTTON, 0),
                               (settings.TOPIC_LIGHT_SENSOR, 0),
                               (settings.TOPIC_CONDITIONER, 0)])  # Add the conditioner topic here

    def on_message(mqtt_client, userdata, msg):
        print(f"Message received on topic {msg.topic} with payload {msg.payload}")

        collection_name = msg.topic.rsplit('/', 1)[-1]  # Extract the last part of the topic after the last slash
        collection = db[collection_name]

        try:
            data = json.loads(msg.payload.decode("utf-8"))
            collection.insert_one(data)
            print(f"Just published {data} to collection {collection_name}")

            # Process the data and send warning/alarm messages if applicable
            if collection_name == 'temperature_humidity':
                process_temperature_humidity(data, msg.topic)
            elif collection_name == 'button':
                process_button(data, msg.topic)
            elif collection_name == 'light':
                process_light(data, msg.topic)
            elif collection_name == 'conditioner':
                process_conditioner(data, msg.topic)

        except json.JSONDecodeError:
            print(f"Invalid JSON payload received for topic {msg.topic}")

    def process_temperature_humidity(data, topic):
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        error_message = None
        # Check temperature and humidity conditions and send warning/alarm messages
        if temperature > settings.TEMPERATURE_THRESHOLD_HIGH:
            error_message = "Warning: High Temperature"
        elif temperature < settings.TEMPERATURE_THRESHOLD_LOW:
            error_message = "Warning: Low Temperature"
        send_error_message(error_message, topic)
        error_message = None
        if humidity > settings.HUMIDITY_THRESHOLD_HIGH:
            error_message = "Warning: High Humidity"
        elif humidity < settings.HUMIDITY_THRESHOLD_LOW:
            error_message = "Warning: Low Humidity"
        if error_message:
            send_error_message(error_message, topic)

    def process_button(data, topic):
        button_state = data.get('button_state')

        # Check button state and send warning/alarm messages if button is pressed
        if button_state:
            send_error_message("Warning: Button is ON", topic)

    def process_light(data, topic):
        intensity = data.get('intensity')

        # Check light intensity condition and send warning/alarm message if intensity is too high
        if intensity > settings.LIGHT_INTENSITY_THRESHOLD:
            send_error_message("Warning: High Light Intensity", topic)

    def process_conditioner(data, topic):
        temperature = data.get('temperature')
        status = data.get('status')
        error_message = None
        # Check temperature and status conditions and send warning/alarm messages if applicable
        if temperature > settings.TEMPERATURE_THRESHOLD_HOT and status == 'Cooling':
            error_message = "Warning: Changed to Cooling cause Temperature is High"
        elif temperature < settings.TEMPERATURE_THRESHOLD_COLD and status == 'Heating':
            error_message = "Warning: Changed to Heating cause Temperature is Low"
        if error_message:
            send_error_message(error_message, topic)

    def send_error_message(message, topic):
        # Create a dictionary to hold the warning message and original topic
        print('send_error_message')
        data = {
            "message": message,
            "topic": topic
        }

        # Convert the dictionary to JSON
        json_data = json.dumps(data)

        # Implement the logic to send the warning/alarm message
        mqtt_client.publish(settings.TOPIC_WARNING_ALARM, json_data)
        print(f"Just published {json_data} to topic {settings.TOPIC_WARNING_ALARM}")

    # MQTT Setup
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    run_data_manager()
