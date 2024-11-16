import pymongo
import csv
import json
import paho.mqtt.client as mqtt
from datetime import datetime

"""
# FILE MANAGEMENT: get deployment ID for topic subscriptions
"""
# file_path = 'iot_project\hub_node\hub_node.csv'
with open("config.txt", "r") as file:
    deployment_id = file.readline()

"""
# DATABASE CONNECTION: PyMongo client to be shared globally
"""
CONN_STRING = "mongodb+srv://visionstitch_dev:LosHermanos58@lospi.usv87.mongodb.net/?retryWrites=true&w=majority&appName=lospi"
cluster = pymongo.MongoClient(
    CONN_STRING,
    server_api=pymongo.server_api.ServerApi(
        version="1", strict=True, deprecation_errors=True
    ),
    tls=True,
)

# Two collections - one for room node check-ins & one for parking
check_ins_collection = cluster["lospi-db"]["check_ins"]
parking_check_ins_collection = cluster["lospi-db"]["parking_check_ins"]

"""
# Logs a check in - called when a message is received on the "room" topic
"""
def log_check_in(check_in):
    current_time = datetime.now()
    # Find rows which haven't got a check_out_time (still checked in)
    filter = {
        "matriculation_no": check_in["_has_result"]["matric"],
        "room": check_in["has_result"]["room"],
        "check_out_time": {"$in": [None, ""]},
    }
    update = {"$set": {"check_out_time": current_time}}
    # Try to set the check_out_time
    update_res = check_ins_collection.update_one(filter, update)

    # If there isn't any such row, it logically must be a new check-in
    # Insert a new row with a blank check_out_time
    if update_res.matched_count == 0:
        new_check_in = {
            "matriculation_no": check_in["_has_result"]["matric"],
            "room": check_in["_has_result"]["room"],
            "check_in_time": current_time,
            "check_out_time": "",
        }

        insert_result = check_ins_collection.insert_one(new_check_in)


"""
# MQTT functions
"""
def mqtt_start():
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()

    return mqtt_client


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connection success")
        client.subscribe(f"{deployment_id}/room")
        client.subscribe(f"{deployment_id}/parking")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        print(f"Error processing message: {e}")

    # If the message is not on the parking topic
    if msg.topic == f"{deployment_id}/room":
        log_check_in(data)


"""
# Connection management - bring MQTT into global scope
"""
mqtt_client = mqtt_start()


def read_from_csv(file_path):
    rooms = {}
    with open(file_path, mode="r") as file:
        counter = csv.reader(file)
        next(counter)
        for row in counter:
            room_id = row[0]
            person_ids = row[1].split(",")
            names = row[2].split(",")
            rooms[room_id] = {"person_ids": person_ids, "names": names}
    return rooms


def roomlist(file_path):
    rooms = read_from_csv(file_path)
    for room_id, data in rooms.items():
        print(f"Room {room_id}:")
        if data["person_ids"] and data["names"]:
            for person_ids, names in zip(data["person_ids"], data["names"]):
                print(f"    - Person ID: {person_ids.strip()}, Name: {names.strip()}")


# roomlist(file_path)
