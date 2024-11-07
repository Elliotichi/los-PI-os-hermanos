from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from helper.observation import Observation
from helper.sensor import SensorNode
from picamera2 import Picamera2

import easyocr
import numpy as np
# import RPi.GPIO as GPIO
import cv2
import imutils
import time
import os
import queue

'''
# Enum representing the "previous" state of the distance sensor
# Prevents spammed photographs of the same car
'''
class CarSensorState(Enum):
    CAR = 1
    NO_CAR = 0

'''
# Parking node is a combination of an ultrasonic distance sensor and camera
# Node's aim is to:
#   - Detect the approach of a vehicle
#   - Scan its registration and perform OCR to get the registration text
#   - Send registration via MQTT
'''
class ParkingNode(SensorNode):
    """
    # Constructor
    """
    def __init__(self):
        self.name = "Parking node"
        super().__init__(Picamera2())
        # super().mqtt_setup(f"{self.deployment_id}/parking")
        self.observed_property = "Car registration"
        self.state = CarSensorState.NO_CAR
        self.dist_threshold = None
        self.GPIO_TRIG = 7
        self.GPIO_ECHO = 11

        # A queue of registrations scanned from images, to be sent via MQTT
        self.results = queue.Queue()

    """
    # ========================================== CONFIGURATION METHODS ==========================================
    # Calibrate the parking node: how close can a vehicle get before the camera takes a photo?
    """
    def calibrate(self):
        self.dist_threshold = float(input("How close is a car to the motion sensor when at rest? "))
        #GPIO.setup(self.GPIO_TRIG, GPIO.OUT)
		#GPIO.setup(self.GPIO_ECHO, GPIO.IN)


    '''
    # ========================================== MEASUREMENT METHODS ==========================================
    '''

    '''
    # Observation function
    # Check a distance sensor for the presence of a new vehicle
    # Capture image (or use sample) & process in a separate thread
    '''
    def observe(self):
        print("Measuring distance...")
        executor = ThreadPoolExecutor(max_workers=1)

        while True:
            # dist = self.ultrasonic_measure()
            # Simulate a car for now
            dist = 20

            # If a car has appeared and stopped at the barrier, start the registration reading process
            if dist<150 and self.state == CarSensorState.NO_CAR:
                print("Detected a car!")
                self.state = CarSensorState.CAR

                executor.submit(self.get_registration)

            elif dist>150 and self.state == CarSensorState.CAR:
                self.state = CarSensorState.NO_CAR

            # See if there are any results waiting for MQTT send
            try:
                reg = self.results.get_nowait()
                print("A result has been processed and is waiting in the queue for MQTT send")
                # publish etc

            except queue.Empty:
                print("The results queue is still empty, nothing to send")
                pass

            time.sleep(1)

    '''
    # Image processing function
    # Noise reduction, edge detection, detect contours & extract the rectangular part
    # (in context, the rectangle will be the license plate)
    # Do OCR on license plate, add to queue
    '''
    def get_registration(self):
        img = self.sensor.capture_array("main")

        cv2.imshow(img)
        cv2.waitKey(0)

        # Tidy up the image: blurring and edge detection
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 200)

        # Extract the set of contours and store the 10 largest (ignore the junk/small shapes)
        contours = imutils.grab_contours(cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE))
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        plateContour = None

        for contour in contours:
            # Calculate the perimeter of the contour
            p = cv2.arcLength(contour, True)

            # Create an approximation (simplify the perimeter contour - usually into a rectangle)
            approx = cv2.approxPolyDP(contour, 0.018 * p, True)

            # If the approximation contour has 4 points, treat it as a license plate
            if len(approx) == 4:
                plateContour = approx
                break

        # Keep only the area within the contour
        if plateContour is not None:
            print("Found a rectangular contour!")
            mask = np.zeros_like(img)
            cv2.drawContours(mask, [plateContour], 0, (255, 255, 255), -1)
            extract_plate = cv2.bitwise_and(img, mask)

            # OCR to get the text of the registration
            reader = easyocr.Reader(["en"])
            result = reader.readtext(extract_plate)

            print(f"Registration is... {result[0][1]}")

            # Add to list of results
            self.results.put(result)


    def ultrasonic_measure(self):
        GPIO.output(self.GPIO_TRIG, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.GPIO_TRIG, GPIO.LOW)

        while GPIO.input(self.GPIO_ECHO) == 0:
            start_time = time.time()

        while GPIO.input(self.GPIO_ECHO) == 1:
            finish_time = time.time()

        return round(((finish_time - start_time) * 1750), 0)