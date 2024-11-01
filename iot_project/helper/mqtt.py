import paho.mqtt.client as mqtt
import ssl
import json

global unique_id
global mqtt_client

'''
# Creates the MQTT client object for the node using the paho library.
'''


'''
# Creates the main MQTT client and returns it.
'''
def rgu_setup(LWT_topic, unique_id):
	# Create the MQTT client object
	mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
	
	# Define the client object's callback behaviors
	mqtt_client.will_set(LWT_topic,json.dumps({"message":"disconnected", "_sender_id":unique_id}), 1, False)
	# Setup TLS for secure transmission								
	mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
	mqtt_client.tls_insecure_set(False)
	mqtt_client.username_pw_set("sociot","s7ci7tRGU")
	mqtt_client.connect("soc-broker.rgu.ac.uk", 8883, 60)
	
	
	return mqtt_client

def eclipse_setup(LWT_topic, unique_id):
    # Create the MQTT client object
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

    # Define the client object's callback behaviors
    mqtt_client.will_set(LWT_topic, json.dumps({"message": "disconnected", "_sender_id": unique_id}), 1, False)

    # Connect to the Eclipse Mosquitto broker
    mqtt_client.connect("test.mosquitto.org", 8883, 60)  # Use "test.mosquitto.org" for public broker

    return mqtt_client


def selector(lwt_topic, unique_id):
      while True:
        print("=== broker setup ===")
        print("1: RGU")
        print("2: Eclipse")
        selection = input("Enter selection")

        if selection == "1":
             client = rgu_setup(lwt_topic, unique_id)
             return client
        
        elif selection == "2":
             client = eclipse_setup(lwt_topic, unique_id)
             return client
        
        else:
             print("invalid selection")

	

