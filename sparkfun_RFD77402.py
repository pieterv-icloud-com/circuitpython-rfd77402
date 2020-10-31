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

class sparkfun_rfd77402: 

    def __init__(self, i2c, address=RFD77402_ADDR):
        self._device = I2CDevice(i2c, address)   

    def begin(self): 
        if (self.get_chip_id() < 0xAD00):
            return False # Chip ID failed. Should be 0xAD01 or 0xAD02

        if (not self.goto_standby_mode()): 
            return False # Chip timed out before going to standby

        # Drive INT_PAD high
        setting = self._read(_RFD77402_ICSR)
        setting &= 0b11110000 # clears writable bits
        self._write(_RFD77402_ICSR, setting)
        setting = self._read(_RFD77402_INTERRUPTS)
        setting &= 0b00000000; # Clears bits
        self.write(_RFD77402_INTERRUPTS, setting)

        # Configure I2C Interface
        self._write16(_RFD77402_CONFIGURE_I2C, 0x65) # 0b.0110.0101 = Address increment, auto increment, host debug, MCPU debug

        # Set initialization - Magic from datasheet. Write 0x05 to 0x15 location.
        self._write_16(_RFD77402_CONFIGURE_PMU, 0x0500) # 0b.0000.0101.0000.0000 //Patch_code_id_en, Patch_mem_en

        if (not self.goto_offmode()):
            return False # MCPU never turned off

        # Read Module ID
        # Skipped

        # Read Firmware ID
        #Skipped

        # Set initialization - Magic from datasheet. Write 0x06 to 0x15 location.
        self._write_16(_RFD77402_CONFIGURE_PMU, 0x0600) # MCPU_Init_state, Patch_mem_en

        if (not self.goto_on_mode()):
            return False # MCPU never turned on

        # ToF Configuration
        # self.write_16(_RFD77402_CONFIGURE_A, 0xE100); # 0b.1110.0001 = Peak is 0x0E, Threshold is 1.
        self.set_peak(0x0E) # Suggested values from page 20
        self.set_threshold(0x01)

        self._write_16(_RFD77402_CONFIGURE_B, 0x10FF)    # Set valid pixel. Set MSP430 default config.
        self._write_16(_RFD77402_CONFIGURE_HW_0, 0x07D0) # Set saturation threshold = 2,000.
        self._write_16(_RFD77402_CONFIGURE_HW_1, 0x5008) # Frequecy = 5. Low level threshold = 8.
        self._write_16(_RFD77402_CONFIGURE_HW_2, 0xA041) # Integration time = 10 * (6500-20)/15)+20 = 4.340ms. Plus reserved magic.
        self._write_16(_RFD77402_CONFIGURE_HW_3, 0x45D4) # Enable harmonic cancellation. Enable auto adjust of integration time Plus reserved magic.

        if (not self.goto_standby_mode()): 
            return False # Error - MCPU never went to standby

        # Whew! We made it through power on configuration

        # Get the calibration data via the 0x0006 mailbox command
        # self.get_calibration_data() # Skipped
        
        # Put device into Standby mode
        if (not self.goto_standby_mode()):
            return False # Error - MCPU never went to standby

        # Now assume user will want sensor in measurement mode

        # Set initialization - Magic from datasheet. Write 0x05 to 0x15 location.
        self._write_16(_RFD77402_CONFIGURE_PMU, 0x0500) # Patch_code_id_en, Patch_mem_en

        if (not self.goto_off_mode()):
            return False # Error - MCPU never turned off

        # Write calibration data
        # Skipped

        # Set initialization - Magic from datasheet. Write 0x06 to 0x15 location.
        self._write_16(_RFD77402_CONFIGURE_PMU, 0x0600) # MCPU_Init_state, Patch_mem_en

        if ( not self.goto_on_mode()):
            return False # Error - MCPU never turned on

        return True

    # Takes a single measurement and sets the global variables with new data
    def take_measurement(self): 
        pass

    # Returns the local variable to the caller
	def get_distance(self):
        return 0

	# Returns the number of valid pixels found when taking measurement
    def get_valid_pixels(self):
        pass

	# Returns the qualitative value representing how confident the sensor is about its reported distance
    def get_confidence_value(self):
        pass

	# Returns the qualitative value representing how confident the sensor is about its reported distance
    def get_mode(self):
        pass

	# Tell MCPU to go to standby mode. Return true if successful
    def goto_standby_mode(self):
        pass

	# Tell MCPU to go to off state. Return true if successful
    def goto_off_mode(self):
        pass

	# Tell MCPU to go to on state. Return true if successful
    def goto_nn_mode(self):
        pass

	# Tell MCPU to go to measurement mode. Takes a measurement. If measurement data is ready, return true
    def goto_measurement_mode(self):
        pass
	
	# Returns the VCSEL peak 4-bit value
    def get_peak(self):
        pass

	# Sets the VCSEL peak 4-bit value
    def set_peak(self, peakValue):
        pass

	# Returns the VCSEL Threshold 4-bit value
    def get_threshold(self):
        pass

	#Sets the VCSEL Threshold 4-bit value
    def set_threshold(self, threshold):
        pass

	# Returns the VCSEL Frequency 4-bit value
    def get_frequency(self):
        pass

	# Sets the VCSEL Frequency 4-bit value
    def set_frequency(self, threshold):
        pass 

	# Gets whatever is in the 'MCPU to Host' mailbox. Check ICSR bit 5 before reading.
    def get_mailbox(self):
        pass
        
    # Software reset the device
	def reset(self):
        pass

	# Returns the chip ID. Should be 0xAD01 or higher.
    def get_chip_id(self):
        pass

	# Retreive 2*27 bytes from MCPU for computation of calibration parameters
	# Reads 54 bytes into the calibration[] array
	# Returns true if new cal data is loaded
	def get_calibration_data(self):
        pass

    # Reads two bytes from a given location from the RFD77402
	def _read_16(self, address):
        # Read and return a 16-bit unsigned big endian value read from the
        # specified 16-bit register address.
        with self._device:
            self._device.write(bytes([(address >> 8) & 0xFF, address & 0xFF]), stop=False)
            result = bytearray(2)
            self._device.read_into(result)
            return (result[0] << 8) | result[1]
	
    # Reads from a given location from the RFD77402
    def _read(self, address):        
        # Read and return a byte from the specified 16-bit register address.
        with self._device:
            self._device.write(bytes([(address >> 8) & 0xFF, address & 0xFF]), stop=False)
            result = bytearray(1)
            self._device.read_into(result)
            return result[0]

	# Write a 16 bit value to a spot in the RFD77402
    def _write_16(self, address, data):
        # Write a 16-bit big endian value to the specified 16-bit register
        # address.
        with self._device:
            self._device.write(bytes([(address >> 8) & 0xFF, address & 0xFF, (data >> 8) & 0xFF, data & 0xFF]))

    # Write a value to a spot in the RFD77402
	def _write(self, address, data):
        # Write 1 byte of data from the specified 16-bit register address.
        with self._device:
            self._device.write(bytes([(address >> 8) & 0xFF, address & 0xFF, data]))
    
    # Variables
	_distance = 0
	_validPixels = 0
	_confidenceValue = 0
	# _calibrationData[54] # Loaded by the 0x006 mailbox command
