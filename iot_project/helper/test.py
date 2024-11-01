def eclipse_setup(LWT_topic, unique_id):
    # Create the MQTT client object
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

    # Define the client object's callback behaviors
    mqtt_client.will_set(LWT_topic, json.dumps({"message": "disconnected", "_sender_id": unique_id}), 1, False)

    # Connect to the Eclipse Mosquitto broker
    mqtt_client.connect("test.mosquitto.org", 8883, 60)  # Use "test.mosquitto.org" for public broker

    return mqtt_client


