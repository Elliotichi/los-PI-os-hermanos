import helper.mqtt as mqtt
from helper.observation import Observation
from helper.sensor import SensorNode
from mfrc522 import MFRC522
import spidev
import RPi.GPIO as GPIO
import time
import sys

class room_node(SensorNode) :
    def __init__(self):
        self.unique_id = 666
        self.room_number = self.calibrate()
        super().__init__(MFRC522())
        self.observed_property = "Room Occupation"
        self.mqtt_client = mqtt.selector("lospi-os/room/shutdown",self.unique_id)
        self.card_present = False
        self.previous_uid = None


    '''
    def calibrate() function should go here.
    '''
    def calibrate(self):
       pass
        # Empty - no calibration required, as the room number/name is part of super().name()


    '''
    Observation function
    '''
    def observe(self):
        try:
            print("Waiting for a tag...")

            # Event loop
            while True:
                self.request_tag()
                self.read_from_tag()
        except KeyboardInterrupt:
            self.sensor.StopAuth()
            GPIO.cleanup()
            sys.exit()


    def request_tag(self):
        reader = self.sensor
        (status, TagType) = reader.Request(reader.PICC_REQIDL)

        if status == reader.MI_OK:
            (status, uid) = reader.Anticoll()
            if status == reader.MI_OK and uid != self.previous_uid:
                print(f"UID is {uid}")
                self.card_present = True
                self.previous_uid = uid

                reader.SelectTag(uid)

                print("Authenticating...")
                status = reader.Authenticate(reader.PICC_AUTHENT1A, 11, [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7], uid)
                print("Done w auth")



    def read_from_tag(self):

        reader = self.sensor
        blocks = [8, 9, 10]
        data = []
        for block_num in blocks:
            block_data = reader.ReadTag(block_num)
            if block_data:
                data+=block_data
                print("Reading...")
        if data:
            print("".join(chr(i) for i in data))

        reader.StopAuth()
        GPIO.cleanup()







