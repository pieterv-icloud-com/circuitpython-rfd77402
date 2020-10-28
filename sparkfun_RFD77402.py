import board
from adafruit_bus_device.i2c_device import I2CDevice

RFD77402_ADDR                   = const(0x4C) # 7-bit unshifted default I2C Address

# Register addresses

_RFD77402_ICSR                   = const(0x00)
_RFD77402_INTERRUPTS             = const(0x02)
_RFD77402_COMMAND                = const(0x04)
_RFD77402_DEVICE_STATUS          = const(0x06)
_RFD77402_RESULT                 = const(0x08)
_RFD77402_RESULT_CONFIDENCE      = const(0x0A)
_RFD77402_CONFIGURE_A            = const(0x0C)
_RFD77402_CONFIGURE_B            = const(0x0E)
_RFD77402_HOST_TO_MCPU_MAILBOX   = const(0x10)
_RFD77402_MCPU_TO_HOST_MAILBOX   = const(0x12)
_RFD77402_CONFIGURE_PMU          = const(0x14)
_RFD77402_CONFIGURE_I2C          = const(0x1C)
_RFD77402_CONFIGURE_HW_0         = const(0x20)
_RFD77402_CONFIGURE_HW_1         = const(0x22)
_RFD77402_CONFIGURE_HW_2         = const(0x24)
_RFD77402_CONFIGURE_HW_3         = const(0x26)
_RFD77402_MOD_CHIP_ID            = const(0x28)

_RFD77402_MODE_MEASUREMENT       = const(0x01)
_RFD77402_MODE_STANDBY           = const(0x10)
_RFD77402_MODE_OFF               = const(0x11)
_RFD77402_MODE_ON                = const(0x12)

_CODE_VALID_DATA                 = const(0x00)
_CODE_FAILED_PIXELS              = const(0x01)
_CODE_FAILED_SIGNAL              = const(0x02)
_CODE_FAILED_SATURATED           = const(0x03)
_CODE_FAILED_NOT_NEW             = const(0x04)
_CODE_FAILED_TIMEOUT             = const(0x05)

_I2C_SPEED_STANDARD              = const(100000)
_I2C_SPEED_FAST                  = const(400000)

class sparkfun_RFD77402: 

    def __init__(self, i2c, address=RFD77402_ADDR):
        self._device = I2CDevice(i2c, address)    
    

