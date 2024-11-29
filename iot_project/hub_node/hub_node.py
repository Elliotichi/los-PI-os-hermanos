import pymongo
import csv
import json
import paho.mqtt.client as mqtt
import datetime
import os

from dotenv import load_dotenv

# FILE MANAGEMENT: get the deployment id from config file
# file_path = 'iot_project\hub_node\hub_node.csv'

load_dotenv()
deployment_id = os.getenv("DEPLOYMENT_NAME")
CONN_STRING = os.getenv("CONN_STRING")

cluster = pymongo.MongoClient(
    CONN_STRING,
    server_api=pymongo.server_api.ServerApi(
        version="1", strict=True, deprecation_errors=True
    ),
    tls=True,
)

# Two collections - one for room node check-ins & one for parking
check_ins_collection = cluster["lospi-db"]["check_ins"]
parking_check_ins_collection = cluster["lospi-db"]["parking"]


def log_parking_check_in(check_in):
    """
    Logs a parking check-in - called when a message is received on the "parking" topic
    :param check_in: a dictionary containing the MQTT payload
    """
    print("Received a parking check-in")
    current_time = datetime.datetime.now()
    filter = {
        "registration": check_in["_has_result"]["registration"],
        "check_out_time": {"$in": [None, ""]},
    }

    update = {"$set": {"check_out_time": current_time}}

    # Try to set the check_out_time
    update_res = parking_check_ins_collection.update_one(filter, update)

    # If there isn't any such row, it must be a new check-in
    # Insert a new row with a null check_out_time
    if update_res.matched_count == 0:
        new_check_in = {
            "registration": check_in["_has_result"]["registration"],
            "check_in_time": current_time,
            "check_out_time": None,
        }

        insert_res = parking_check_ins_collection.insert_one(new_check_in)


def log_check_in(check_in):
    """
    Logs a room check-in - called when a message is received on the "room" topic
    :param check_in: a dictionary containing the MQTT payload
    """
    print("Received a check-in")
    current_time = datetime.datetime.now()

    # Find rows which haven't got a check_out_time (still checked in)
    filter = {
        "matriculation_no": check_in["_has_result"]["student"]["matriculation_no"],
        "room": check_in["_has_result"]["room"],
        "check_out_time": {"$in": [None, ""]},
    }
    update = {"$set": {"check_out_time": current_time}}

    # Try to set the check_out_time
    update_res = check_ins_collection.update_one(filter, update)

    # If there isn't any such row, it must be a new check-in
    # Insert a new row with a null check_out_time
    if update_res.matched_count == 0:
        new_check_in = {
            "matriculation_no": check_in["_has_result"]["student"]["matriculation_no"],
            "first_name": check_in["_has_result"]["student"]["first_name"],
            "last_name": check_in["_has_result"]["student"]["last_name"],
            "room": check_in["_has_result"]["room"],
            "check_in_time": current_time,
            "check_out_time": None,
        }

        insert_res = check_ins_collection.insert_one(new_check_in)


def mqtt_start():
    """
    Creates and starts client loop for an MQTT client
    """
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("test.mosquitto.org", 1883, 10)
    mqtt_client.loop_start()
    return mqtt_client


def on_connect(client, userdata, flags, rc):
    """
    # Connection callback - when connected, subscribe to these topics
    :param client: the paho.mqtt.client object
    :param rc: the result code from connecting (0 = Success, 1 = Error, 2 = Error . . .)
    """
    if rc == 0:
        print("Connection success")
        client.subscribe(f"{deployment_id}/room")
        client.subscribe(f"{deployment_id}/parking")


def on_message(client, userdata, msg):
    """
    Message callback - if a room message is received, log a room check in, vice versa for parking
    :param msg: dictionary containing the MQTT payload
    """
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        print(f"Error processing message: {e}")

    # If the message is not on the parking topic
    if msg.topic == f"{deployment_id}/room":
        log_check_in(data)

    if msg.topic == f"{deployment_id}/parking":
        # Log a parking check-in
        pass

    # Bring MQTT into global scope

log_parking_check_in(
    {
        "hi" : "hiya", 
        "_has_result" : {"registration":"AB25 5BZ"},
    }
)

mqtt_client = mqtt_start()

while True:
    pass
