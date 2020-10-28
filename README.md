# RFD77402

CircuitPython sample for using the [RFD77402](https://www.sparkfun.com/products/retired/14539) distance sensor on the ESP32-S2.

## ESP32-S2 Instructions

Display some text on a i2c oled display using the esp32 s2.

[Getting Started](https://gist.github.com/askpatrickw/0a276c7e2d4f54e442b2cb6eaa0d32ea)

### Reinstall esptool from esp-idf

```bash
pip install -e ~/esp/esp-idf/components/esptool_py/esptool
```

### Erase

```bash
esptool.py --chip esp32s2 --port /dev/tty.SLAB_USBtoUART3 -b 460800 erase_flash
```

### Flash

```bash
esptool.py --chip esp32s2 --port /dev/tty.SLAB_USBtoUART3 -b 460800 --before=default_reset --after=hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 4MB 0x0000 ~/downloads/adafruit-circuitpython-espressif_saola_1_wroom-en_US-6.0.0-rc.0.bin
```

### Connect to REPL

```bash
screen /dev/tty.usbmodem7CDFA100994C1 115200
```

