# RFD77402

CircuitPython sample for using the [RFD77402](https://www.sparkfun.com/products/retired/14539) distance sensor on the ESP32-S2. Converted the code from [here](https://github.com/sparkfun/SparkFun_RFD77402_Arduino_Library).

## Parts

[ESP32 S2 Wroom-I 4M](https://www.robotics.org.za/ESP32-S2-WROOM-I?search=wroom)

[Adafruit USB C Breakout](https://www.robotics.org.za/AF4090?search=usb%20c%20breakout)

[Qwiic Cable - Female Jumper (4-Pin)](https://www.robotics.org.za/CAB-14988?search=qwiic%20femal)

[Qwiic Distance Sensor - RFD77402](https://www.robotics.org.za/SEN-14539?search=qwiic%20distance)

## Wiring

### USB C > ESP32

|Source|Destination|
| ---- | --------- |
|D+|18|
|D-|19|
|VBUS|5V|
|GND|GND|

### ESP32 > QWIIC

|Source|Destination|
| ---- | --------- |
|3V3|Red|
|GND|Black|
|9|Yellow|
|8|Blue|

## ESP32-S2

### Reinstall esptool from esp-idf

```bash
pip install -e ~/esp/esp-idf/components/esptool_py/esptool
```

### Erase

```bash
esptool.py --chip esp32s2 --port /dev/tty.SLAB_USBtoUART3 -b 460800 erase_flash
```

### Flash with CircuitPython 6.0.0 RC 1

```bash
esptool.py --chip esp32s2 --port /dev/tty.SLAB_USBtoUART3 -b 460800 --before=default_reset --after=hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 4MB 0x0000 ~/downloads/adafruit-circuitpython-espressif_saola_1_wroom-en_US-6.0.0.bin
```

### Connect to REPL

```bash
screen /dev/tty.usbmodem7CDFA100994C1 115200
```

### Wifi

[Internet Connect!](https://learn.adafruit.com/adafruit-metro-esp32-s2/internet-connect)


