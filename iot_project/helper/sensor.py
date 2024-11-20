import json
import time
import helper.mqtt as mqtt
import os

from dotenv import load_dotenv

"""
# Top level class for all sensor nodes (standardizes implementation)
"""


class SensorNode:
    load_dotenv()
    def __init__(self, sensor):
        """
        Initializes properties common to all node types
        :param sensor: an object representing the sensor (GPIO, PiCamera2, etc)
        """
        self.name = self.name_sensor()
        self.sensor = sensor
        
        self.observed_property = None
        self.feature_of_interest = None

        self.deployment_id = os.getenv("DEPLOYMENT_NAME")

        self.mqtt_client = mqtt.eclipse_setup()

    def name_sensor(self):
        return input("Name this sensor: ")

    def calibrate(self):
        raise NotImplementedError(
            "Subclasses of SensorNode should have their own calibrate() method"
        )

    def observe(self):
        raise NotImplementedError(
            "Subclasses of SensorNode should have their own observe() method"
        )
