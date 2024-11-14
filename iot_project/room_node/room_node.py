import helper.mqtt as mqtt
from helper.observation import Observation
from helper.sensor import SensorNode
from helper.mfrc522raw import MFRC522
import spidev
import RPi.GPIO
import time
import random

class room_node(SensorNode) :
    def __init__(self):
        self.unique_id = random.randint(1, 10000000) 
        super().__init__(MFRC522())
        self.observed_property = "Room Occupation"
        self.mqtt_client = mqtt.selector("lospi-os/room/shutdown",self.unique_id)

        # Internal state variables used to streamline NFC reading
        # User might place card on the reader for too long, leading to an immediate check-in and check-out
        self._previous_uid = None
        self._card_present = False


    '''
    def calibrate() function should go here.
    '''
    def calibrate(self):
        room = input("What is the room number?")
        self.observed_property = room+" occupancy"

    '''
    Observation function
    '''
    def observe(self):
        status = self.poll_and_auth()
        if status == 1:
            tag_data = self.read_from_tag()
            
            obs = Observation(
                _sender_id = self.unique_id,
                _sender_name = self.name,
                _feature_of_interest = self.feature_of_interest,
                _observed_property = self.observed_property,
                _haxs_result = {"value": tag_data, "units": "string"}   
            )
            
            self.mqtt_client.publish(f"{self.deployment_id}/{self.room}", obs.to_mqtt_payload())

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


    def read_from_tag(self):
        reader = self.sensor

        blocks = [8, 9, 10]
        data = []
        for block_num in blocks:
            block_data = reader.ReadTag(block_num)
            if block_data:
                data+=block_data
        print("".join(chr(i) for i in data))
        time.sleep(5000)

        return data



