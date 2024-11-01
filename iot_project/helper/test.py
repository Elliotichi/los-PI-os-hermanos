import json
import ssl

import paho.mqtt.client as mqtt

def eclipse_setup(LWT_topic, unique_id):
    # Create the MQTT client object
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect

    # Define the client object's callback behaviors
    mqtt_client.will_set(LWT_topic, json.dumps({"message": "disconnected", "_sender_id": unique_id}), 1, False)

    # Connect to the Eclipse Mosquitto broker
    mqtt_client.connect("test.mosquitto.org", 8883, 60)  # Use "test.mosquitto.org" for public broker

    return mqtt_client

def on_connect(client):
    topic = "lospi-os/room"
    client.subscribe(topic)
    print(f"Subscribed to topic: {topic}")
    return

    # Define the callback for when a message is received
    client.on_message = on_message

def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

# Example usage
if __name__ == "__main__":
    client = eclipse_setup("your/lwt/topic", "unique_id_123")
    if client:
        # Start the MQTT client loop to process network traffic and callbacks
        client.loop_start()

        # Keep the script running to listen for messages
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Disconnecting...")
            client.loop_stop()
            client.disconnect()


