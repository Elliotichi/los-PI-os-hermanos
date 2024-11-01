import json
import ssl

import paho.mqtt.client as mqtt

def eclipse_setup(LWT_topic, unique_id):
    # Create the MQTT client object
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
        # Define the client object's callback behaviors
    mqtt_client.will_set(LWT_topic, json.dumps({"message": "disconnected", "_sender_id": unique_id}), 1, False)

    # Connect to the Eclipse Mosquitto broker
    mqtt_client.connect("test.mosquitto.org", 8883, 60)  # Use "test.mosquitto.org" for public broker
    mqtt_client.loop_start()
    return mqtt_client

def on_mqtt_message(client, userdata, msg):
    print("message recieved")
    msg = json.loads(msg.payload.decode("utf-8"))   
    print(msg) 

def on_mqtt_connect(client, userdata, flags, rc):
	client.subscribe("lospi-os/room")

client = eclipse_setup("lospi-os/room",2222)
client.loop_start()