import time
import board
import busio
import sparkfun_rfd77402
from sparkfun_rfd77402 import RFD77402_ADDR

import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to %s"%secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print(print("Connected to %s!"%secrets["ssid"]))
print("My IP address is", wifi.radio.ipv4_address)

topic = "kitchen/ivy"

# Initialize MQTT interface with the esp interface
# MQTT.set_socket(socket, esp)

# Set up a MiniMQTT Client
client = MQTT.MQTT(
    broker=secrets["broker"], username=secrets["user"], password=secrets["pass"], port=1883
)

print("Attempting to connect to %s" % client.broker)
client.connect()

client.ping()

print("Publishing to %s" % topic)
client.publish(topic, "Hello Broker!")

print("Disconnecting from %s" % client.broker)
client.disconnect()

displayio.release_displays()

i2c = busio.I2C(sda=board.IO8, scl=board.IO9)

proximity_bus = sparkfun_rfd77402.rfd77402(i2c=i2c, address=RFD77402_ADDR, debug=True)

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 32  # Change to 64 if needed

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

if proximity_bus.begin():
    while True:
        distance = proximity_bus.distance
        pixels = proximity_bus.pixels
        confidence = proximity_bus.confidence

        # Make the display context
        splash = displayio.Group(max_size=10)
        display.show(splash)

        color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(bg_sprite)

        # Distance
        text = "Distance:" + str(distance) + " mm"
        text_area = label.Label(terminalio.FONT, text=text, color=0x000000, x=2, y=HEIGHT // 3 - 1)

        splash.append(text_area)

        # Pixels
        text = "Pixels:" + str(pixels)
        text_area = label.Label(terminalio.FONT, text=text, color=0x000000, x=2, y=(HEIGHT // 3 - 1) * 2)

        splash.append(text_area)

        # Confidence
        text = "Confidence:" + str(pixels)
        text_area = label.Label(terminalio.FONT, text=text, color=0x000000, x=2, y=(HEIGHT // 3 - 1) * 3)

        splash.append(text_area)

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

