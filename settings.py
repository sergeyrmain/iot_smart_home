# MQTT settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# MQTT topics
TOPIC_TEMPERATURE_HUMIDITY = "house/room_simulator/sensor/temperature_humidity"
TOPIC_BUTTON = "house/room_simulator/switch/button"
TOPIC_LIGHT_SENSOR = "house/room_simulator/sensor/light"
TOPIC_CONDITIONER = "house/room_simulator/switch/conditioner"  # New topic for the conditioner

# MongoDB settings
MONGO_URI = "mongodb+srv://sergio44kk:AnvmxKe2Gs14BaYI@iotsergey.yexpbgl.mongodb.net/?retryWrites=true&w=majority"
MONGO_DATABASE = "IOTsergey"

# Sensor collections
MONGO_COLLECTIONS = {
    'temperature_humidity': {
        'topic': 'house/room_simulator/sensor/temperature_humidity',
        'collection': 'temperature_humidity',
        'keys': ['temperature', 'humidity'],
        'name': 'Temperature and Humidity'
    },
    'button': {
        'topic': 'house/room_simulator/switch/button',
        'collection': 'button',
        'keys': ['button_state'],
        'name': 'Button'
    },
    'light': {
        'topic': 'house/room_simulator/sensor/light',
        'collection': 'light',
        'keys': ['intensity'],
        'name': 'Light Sensor'
    },
    'conditioner': {
        'topic': 'house/room_simulator/switch/conditioner',
        'collection': 'conditioner',
        'keys': ['temperature', 'status'],
        'name': 'Air Conditioner'
    }
}
TOPIC_WARNING_ALARM = 'house/room_simulator/warnings'


gui_labels = {
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'intensity': 'Light Intensity',
    'button_state': 'Button State',
    'conditioner_temperature': 'Conditioner Temperature'
}


# Emulator settings
TEMP_RANGE = (15, 30)
HUMIDITY_RANGE = (20, 90)
LIGHT_INTENSITY_RANGE = (0, 100)
BUTTON_STATES = ["ON", "OFF"]

# Sensor keys
TEMPERATURE_KEY = "temperature"
HUMIDITY_KEY = "humidity"
LIGHT_LEVEL_KEY = "intensity"
BUTTON_STATE_KEY = "button_state"
CONDITIONER_TEMPERATURE_KEY = "temperature"  # Key for conditioner temperature

# Conditioner settings
TEMPERATURE_THRESHOLD_HOT = 25  # Threshold temperature for cooling
TEMPERATURE_THRESHOLD_COLD = 18  # Threshold temperature for heating
LIGHT_INTENSITY_THRESHOLD = 50  # Threshold for light intensity
TEMPERATURE_THRESHOLD_HIGH = 35  # Threshold for high temperature
TEMPERATURE_THRESHOLD_LOW = 10  # Threshold for low temperature
HUMIDITY_THRESHOLD_HIGH = 80  # Threshold for high humidity
HUMIDITY_THRESHOLD_LOW = 30  # Threshold for low humidity