import time
import board
import busio
import sparkfun_rfd77402
from sparkfun_rfd77402 import RFD77402_ADDR

i2c = busio.I2C(sda=board.IO8, scl=board.IO9)

proximity_bus = sparkfun_rfd77402.rfd77402(i2c=i2c, address=RFD77402_ADDR, debug=True)

if proximity_bus.begin():
    while True:
        distance = proximity_bus.distance
        pixels = proximity_bus.pixels
        confidence = proximity_bus.confidence

        print("distance:", distance, "mm pixels:", pixels, "confidence:", confidence, "\n", sep=" ")

        if distance == sparkfun_rfd77402.CODE_FAILED_PIXELS:
            print("Not enough pixels valid")
            proximity_bus.goto_off_mode()
        if distance == sparkfun_rfd77402.CODE_FAILED_SIGNAL:
            print("Not enough signal")
            proximity_bus.goto_off_mode()
        if distance == sparkfun_rfd77402.CODE_FAILED_SATURATED:
            print("Sensor pixels saturated")
            proximity_bus.goto_off_mode()
        if distance == sparkfun_rfd77402.CODE_FAILED_NOT_NEW:
            print("New measurement failed")
            proximity_bus.goto_off_mode()
        if distance == sparkfun_rfd77402.CODE_FAILED_TIMEOUT:
            print("Sensors timed out")
            proximity_bus.goto_off_mode()

        time.sleep(1)

