import json
import time

'''
# Top level class for all sensor nodes (standardizes implementation)
'''
class SensorNode:
    def __init__(self, sensor):
        self.get_name()
        self.mqtt_client = None
        self.observed_property = None
        self.sensor = sensor

        #with open ("config.txt", "r") as file:
         #   self.deployment_id = file.readLine()




    def get_name(self):
        self.name = input("Name this sensor: ")


    def calibrate(self):
        raise NotImplementedError("Subclasses of SensorNode should have their own calibrate() method")

    def observe(self):
        raise NotImplementedError("Subclasses of SensorNode should have their own observe() method")