import helper.mqtt as mqtt
from helper.observation import Observation
from helper.sensor import SensorNode
from helper.mfrc522raw import MFRC522
import time
import random
import pymongo
import datetime
import os
from dotenv import load_dotenv


class room_node(SensorNode) :
    load_dotenv()
    def __init__(self):
        super().__init__(MFRC522())
        
        
        self.observed_property = "Occupancy levels"

        # Internal state variables used to streamline NFC reading
        # User might place card on the reader for too long, leading to an immediate check-in and check-out
        self._previous_uid = None
        self._card_present = False

        # used to connect to the database of existing students.
        self.cluster = self.setup_mongo()["lospi-db"]
        
        self.cluster["sensor_information"].insert_one({
            "sensor_name": self.name,
            "feature_of_interest": self.feature_of_interest,
            "observed_property":self.observed_property
        })


    '''
    defines the room that the node is attached to 
    '''
    def calibrate(self):
        self.feature_of_interest = input("Enter room number: ")+" occupancy"


    '''
    defines the observation loop
    calls the respective functions
    '''
    def observe(self):
        try:
            while True:
                status = self.poll_and_auth()
                if status == self.sensor.MI_OK:
                    tag_data, validate = self.read_from_tag()
                    self.sensor.StopAuth()
                
                    #if tag_data is not None:
                        #data_to_send, validate = make_student_obj(tag_data)
                    if validate == True:
                        obs = Observation(
                            _sender_id = self.name,
                            _sender_name = self.name,
                            _feature_of_interest = self.feature_of_interest,
                            _observed_property = self.observed_property,
                            _has_result = {
                                "student":tag_data,
                                "room":self.room, 
                                "scan_time":datetime.datetime.now(), 
                                "units": "string"}
                        )
        
                        self.mqtt_client.publish(f"{self.deployment_id}/room", obs.to_mqtt_payload())
                        
        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting...")
            exit()
            
    '''
    establishes a mongoDB
    '''
    def setup_mongo(self):
        # DATABASE: set up a connection, tls enabled, etc
        CONN_STRING = os.getenv("CONN_STRING")
        cluster = pymongo.MongoClient(
            CONN_STRING,
            server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True
            ),
            tls=True,
        )
        return cluster
        
    '''
    authenticates that the RFID tag placed on the reader is valid
    ensures the tag is not the same tag placed before
    '''
    def poll_and_auth(self):
        status = None
        reader = self.sensor

        while status != reader.MI_OK:
            (status, TagType) = reader.Request(reader.PICC_REQIDL)

            if status != reader.MI_OK:
                self._previous_uid = None
                self._card_present = False

            if status == reader.MI_OK:
                (status, uid) = reader.Anticoll()
                if status == reader.MI_OK and uid != self._previous_uid:
                    self._previous_uid = uid
                    self.card_present = True

                    reader.SelectTag(uid)

                    status = reader.Authenticate(reader.PICC_AUTHENT1A, 11, [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7], uid)
                    return status

    '''
    Retrieves data from the RFID tag using the RFID scanner
    '''
    def read_from_tag(self):
        reader = self.sensor

        blocks = [8, 9, 10]

        data = []
        for block_num in blocks:
            block_data = reader.ReadTag(block_num)
            if block_data:
                data+=block_data

        print(data)
        i = 0
        for unicode_val in data:
            data[i] = chr(unicode_val)
            i+=1
        try:
            data = "".join(data[:-1])
            split_data = data.split(",")
            student_number = split_data[1]
            print(student_number)
            student = self.cluster["students"].find_one({"matriculation_no":student_number})
            print(student)
            validate = True
            return student, validate
        
        except:
            print("Tag invalid")





    
