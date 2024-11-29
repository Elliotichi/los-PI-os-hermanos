from concurrent.futures import ThreadPoolExecutor
from enum import Enum


from helper.observation import Observation
from helper.sensor import SensorNode
from picamera2 import Picamera2
from dotenv import load_dotenv

import easyocr
import numpy as np

import cv2
import imutils
import time
import os
import queue
import lgpio
import tracemalloc
import pymongo
import datetime



class CarSensorState(Enum):
    """
    Enum for state management
    """

    CAR = 1
    NO_CAR = 0

GPIO_TRIG = 4
GPIO_ECHO = 17

class ParkingNode(SensorNode):
    """
    Combines an ultrasonic sensor and camera: on approach then take registration photo, do preprocessing & OCR
    """
    load_dotenv()
    CONN_STRING = os.getenv("CONN_STRING")

    def __init__(self):
        """
        Invokes superclass constructor, connects to database
        """
        super().__init__(Picamera2())
        self.observed_property = "Car registration"
        self.state = CarSensorState.NO_CAR

        self.cluster = pymongo.MongoClient(
            ParkingNode.CONN_STRING,
            server_api=pymongo.server_api.ServerApi(
                version="1", strict=True, deprecation_errors=True
            ),
            tls=True,
        )["lospi-db"]
        
        self.cluster["sensor_information"].insert_one(
            {
                "sensor_name": self.name,
                "feature_of_interest": self.feature_of_interest,
                "observed_property": self.observed_property,
            }
        )

        # Queue of registrations scanned from images to be sent via MQTT
        self.results = queue.Queue()

    """
    # ========================================== CONFIGURATION METHODS ==========================================
    """

    def calibrate(self):
        """
        Calibrate the parking node with a distance threshold for approach
        """
        self.dist_threshold = float(input("Vehicle approach threshold: "))
        lgpio.setup(GPIO_TRIG, lgpio.OUT)
        lgpio.setup(GPIO_ECHO, lgpio.IN)



    """
    # ========================================== MEASUREMENT METHODS ==========================================
    """

    def observe(self):
        """
        Main method: wait for an approach, then take photo, process & submit registration
        """
        try:
            executor = ThreadPoolExecutor(max_workers=1)

            while True:
                # Measure distance of an approaching object
                dist = self.ultrasonic_measure()
                 

                # If a car has appeared and stopped at the barrier, start the registration reading process
                if dist < 150 and self.state == CarSensorState.NO_CAR:
                    print("Detected a car!")
                    self.state = CarSensorState.CAR

                    executor.submit(
                        self.process_image, self.sensor.capture_array("main")
                    )

                elif dist > 150 and self.state == CarSensorState.CAR:
                    self.state = CarSensorState.NO_CAR

                # See if there are any results waiting for MQTT send
                try:
                    reg = self.results.get_nowait()
                    print(
                        "A result has been processed and is waiting in the queue for MQTT send"
                    )
                    obs = Observation(
                            _sender_id = self.name,
                            _sender_name = self.name,
                            _feature_of_interest = self.feature_of_interest,
                            _observed_property = self.observed_property,
                            _has_result = {"registration":reg, "units": "string"}
                        )
                    self.mqtt_client.publish(f"{self.deployment_id}/parking", obs.to_mqtt_payload())

                except queue.Empty:
                    pass

                time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting...")
            exit()

    def process_image(self, original_photo):
        """
        Performs the various stages of image processing & recognition
        :param original_photo: a pixel array taken from a PiCamera2
        """
        tracemalloc.start()
        start_snap = tracemalloc.take_snapshot()

        edges = self.image_preprocess(original_photo)
        plate_contours = self.get_image_contours(edges)
        bitmask = self.get_bitmask(plate_contours)
        registration = self.image_ocr(bitmask, original_photo)
        self.queue.put(registration)

        end_snap = tracemalloc.take_snapshot()
        start_stats = start_snap.statistics("lineno")
        end_stats = end_snap.statistics("lineno")
        memory_diff = end_snap.compare_to(start_snap, "lineno")
        total_allocated = sum(stat.size_diff for stat in memory_diff)
        print(
            f"Total memory allocated between snaps: {total_allocated / 1024**2:.2f} MB"
        )

    def image_preprocess(self, photo):
        """
        Processes the image with blur and edge detection
        :param photo: A pixel array
        """
        img = cv2.imread("sample_reg.png")

        # Tidy up the image: blurring and edge detection
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 200)

        return edges

    def get_image_contours(self, edges):
        """
        Extracts and approximates edge contours to find the large rectangular shape
        :param edges: the result of a cv2.Canny call - edge-detected image
        """
        # Extract the set of contours and store the 10 largest (ignore the junk/small shapes)
        contours = imutils.grab_contours(
            cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        )
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

            return plateContour

    def get_bitmask(self, plate_contour, original_image):
        """
        Creates a binary-AND bitmask to extract the license plate
        :param plate_contour: the contour corresponding to the license plate
        :param original_image: the original pixel array captured from PiCamera2
        """
        if plate_contour is not None:
            print("Found a rectangular contour!")
            mask = np.zeros_like(original_image)
            cv2.drawContours(mask, [plate_contour], 0, (255, 255, 255), -1)
            extract_plate = cv2.bitwise_and(original_image, mask)

            return extract_plate

    def image_ocr(self, bitmask):
        """
        Performs OCR image detection
        :param bitmask: pixel array corresponding to the preprocessed registration plate
        """
        # OCR to get the text of the registration
        reader = easyocr.Reader(["en"])
        result = reader.readtext(bitmask)

        return result

    def ultrasonic_measure(self):
        lgpio.output(GPIO_TRIG, lgpio.HIGH)
        time.sleep(0.1)
        lgpio.output(GPIO_TRIG, lgpio.LOW)

        while lgpio.input(self.GPIO_ECHO) == 0:
            start_time = time.time()

        while lgpio.input(self.GPIO_ECHO) == 1:
            finish_time = time.time()

        return round(((finish_time - start_time) * 1750), 0)
