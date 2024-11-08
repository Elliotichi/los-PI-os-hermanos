import RPI.GPIO as GPIO
from mfrc522 import SimpleMFRC522 as nfc

reader = nfc()

try:
    text = input('New data')
    print("place tage to write")
    reader.write(text)
    print("Written")
finally:
     GPIO.cleanup()