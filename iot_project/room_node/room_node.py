import helper.mqtt as mqtt
from helper.observation import Observation

class room_node :
    def __init__(self):
        self.unique_id = 666
        self.room_number = "r533"
        self.observed_property = "Room Occupation"
        self.mqtt_client = mqtt.selector("lospi-os/room/shutdown",self.unique_id)

    '''
    def calibrate() function should go here.
    '''

    '''
    gets sign in from user will be replaced with nfc reader hopefully
    '''
    def sign_in(self):
        first_name = input("enter first name: ")
        last_name = input("enter last name: ")
        student_number = input("enter student number")
        student = {"Value":
                {
                    "first_name" : first_name, 
                    "last_name" : last_name,
                    "student_number" : student_number
                }
            }
        return student
    

    '''
    Observation function, will hopefully be done manually when nfc reader happens
    '''
    def observe(self):
        while True:
            print("========= Select option ========")
            print("1: sign in")
            print("2: close program")
            selection = input("Enter here: ")
            match selection :
                case "1":
                    observation = Observation(
						_sender_id = self.unique_id,
						_sender_name = self.room_number,
						_feature_of_interest = "rgu", 
						_observed_property = self.observed_property,
						_has_result = self.sign_in()
                    )
                    print(observation.__repr__)
                    self.mqtt_client.publish("lospios/room", observation.to_mqtt_payload())
                
                    

                case "2":
                    break

                case _:
                    print("invalid selection")


    
   




    
    