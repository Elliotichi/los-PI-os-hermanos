import helper.mqtt as mqtt
from helper.observation import Observation
from helper.sensor import SensorNode
from helper.mfrc522raw import MFRC522
import spidev
import RPi.GPIO
import time

class room_node(SensorNode) :
    def __init__(self):
        self.unique_id = 666
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
        i = 0
        print(f"Poll {i}")
        self.poll_and_auth()
        time.sleep(0.5)
        i+=1



    def poll_and_auth(self):
        status = None
        reader = self.sensor

        while status != reader.MI_OK:
            (status, TagType) = reader.Request(reader.PICC_REQIDL)

            if status != reader.MI_OK:
                self._previous_uid = None
                self._card_present = False

            if status == reader.MI_OK:
                print("anticoll...")
                (status, uid) = reader.Anticoll()
                if status == reader.MI_OK and uid != self._previous_uid:
                    self._previous_uid = uid
                    print(f"UID is {uid}")
                    self.card_present = True

                    reader.SelectTag(uid)

                    print("Authenticating...")
                    status = reader.Authenticate(reader.PICC_AUTHENT1A, 11, [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7], uid)
                    self.read_from_tag()


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



