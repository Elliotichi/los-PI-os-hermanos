import paho.mqtt.client as mqtt
import ssl
import json

global unique_id
global mqtt_client

"""
# Creates the MQTT client object for the node using the paho library.
"""


def eclipse_setup():
    # Create the MQTT client object
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_mqtt_connect


    # Connect to the Eclipse Mosquitto broker
    mqtt_client.connect(
        "test.mosquitto.org", 1883, 10
    )  # Use "test.mosquitto.org" for public broker
    
    mqtt_client.loop_start()
    return mqtt_client


def on_mqtt_connect():
     print("Connected to broker!")