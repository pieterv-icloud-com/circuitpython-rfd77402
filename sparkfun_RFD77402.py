import board
import time
from micropython import const

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

CODE_VALID_DATA                 = const(0x00)
CODE_FAILED_PIXELS              = const(0x01)
CODE_FAILED_SIGNAL              = const(0x02)
CODE_FAILED_SATURATED           = const(0x03)
CODE_FAILED_NOT_NEW             = const(0x04)
CODE_FAILED_TIMEOUT             = const(0x05)

class rfd77402: 

    def __init__(self, i2c, address=RFD77402_ADDR, debug=False):
        self._device = I2CDevice(i2c, address)   
        self._debug = debug

    def begin(self): 
        if self._debug:
            print("begin()")

        if(self.chip_id < 0xAD00):
            return False # Chip ID failed. Should be 0xAD01 or 0xAD02

        if (not self.goto_standby_mode()): 
            return False # Chip timed out before going to standby

        # Drive INT_PAD high
        setting = self._read(_RFD77402_ICSR)
        setting &= 0b11110000 # clears writable bits
        self._write(_RFD77402_ICSR, setting)
        setting = self._read(_RFD77402_INTERRUPTS)
        setting &= 0b00000000 # Clears bits
        self._write(_RFD77402_INTERRUPTS, setting)

        # Configure I2C Interface
        self._write_16(_RFD77402_CONFIGURE_I2C, 0x65) # 0b.0110.0101 = Address increment, auto increment, host debug, MCPU debug

        # Set initialization - Magic from datasheet. Write 0x05 to 0x15 location.
        self._write_16(_RFD77402_CONFIGURE_PMU, 0x0500) # 0b.0000.0101.0000.0000 //Patch_code_id_en, Patch_mem_en

        if (not self.goto_off_mode()):
            return False # MCPU never turned off

        # Read Module ID
        # Skipped

        # Read Firmware ID
        # Skipped

        # Set initialization - Magic from datasheet. Write 0x06 to 0x15 location.
        self._write_16(_RFD77402_CONFIGURE_PMU, 0x0600) # MCPU_Init_state, Patch_mem_en

        if (not self.goto_on_mode()):
            return False # MCPU never turned on

        # ToF Configuration
        # self.write_16(_RFD77402_CONFIGURE_A, 0xE100) # 0b.1110.0001 = Peak is 0x0E, Threshold is 1.
        self.peak = 0x0E # Suggested values from page 20
        self.threshold = 0x01

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
        if self._debug:
            print("take_measurement()")

        if (not self.goto_measurement_mode()):
            return CODE_FAILED_TIMEOUT # Error - Timeout

        # New data is now available!

        # Read result
        resultRegister = self._read_16(_RFD77402_RESULT)

        if (resultRegister & 0x7FFF): # Reading is valid
            errorCode = (resultRegister >> 13) & 0x03

            if (errorCode == 0):
                self._distance = (resultRegister >> 2) & 0x07FF # Distance is good. Read it.

                # Read confidence register
                confidenceRegister = self._read_16(_RFD77402_RESULT_CONFIDENCE)
                self._validPixels = confidenceRegister & 0x0F
                self._confidenceValue = (confidenceRegister >> 4) & 0x07FF

            return errorCode
        else:
            # Reading is not vald
            return CODE_FAILED_NOT_NEW # Error code for reading is not new

	# Returns the qualitative value representing how confident the sensor is about its reported distance
    @property
    def mode(self):
        if self._debug:
            print("mode()")
        return (self.read(_RFD77402_COMMAND) & 0x3F)        

	# Returns the VCSEL peak 4-bit value
    @property
    def peak(self):
        if self._debug:
            print("peak()")

        configValue = self._read_16(_RFD77402_CONFIGURE_A)
        return ((configValue >> 12) & 0x0F)

    # Sets the VCSEL peak 4-bit value
    @peak.setter
    def peak(self, value):
        if self._debug:
            print("set_peak()")

        configValue = self._read_16(_RFD77402_CONFIGURE_A) # Read
        configValue &= ~0xF000 # Zero out the peak configuration bits
        configValue |= value << 12 # Mask in user's settings
        self._write_16(_RFD77402_CONFIGURE_A, configValue) # Write in this new value

	# Returns the VCSEL Threshold 4-bit value
    @property
    def threshold(self):
        if self._debug:
            print("threshold()")

        configValue = self._read_16(_RFD77402_CONFIGURE_A)
        return ((configValue >> 8) & 0x0F)

	#Sets the VCSEL Threshold 4-bit value
    @threshold.setter
    def threshold(self, value):
        if self._debug:
            print("set_threshold()")

        configValue = self._read_16(_RFD77402_CONFIGURE_A) # Read
        configValue &= ~0x0F00 # Zero out the threshold configuration bits
        configValue |= value << 8 # Mask in user's settings
        self._write_16(_RFD77402_CONFIGURE_A, configValue) # Write in this new value

	# Returns the VCSEL Frequency 4-bit value\
    @property
    def frequency(self):
        if self._debug:
            print("frequency()")

        configValue = self._read_16(_RFD77402_CONFIGURE_HW_1)
        return ((configValue >> 12) & 0x0F)

	# Sets the VCSEL Frequency 4-bit value
    @frequency.setter
    def frequency(self, value):
        if self._debug:
            print("set_frequency()")

        configValue = self._read_16(_RFD77402_CONFIGURE_HW_1) # Read
        configValue &= ~0xF000 # Zero out the threshold configuration bits
        configValue |= value << 12 # Mask in user's settings
        self._write_16(_RFD77402_CONFIGURE_HW_1, configValue) # Write in this new value

    @property
    def distance(self):
        if self._debug:
            print("distance()")

        self.take_measurement()
        return self._distance

	# Gets whatever is in the 'MCPU to Host' mailbox. Check ICSR bit 5 before reading.
    def mailbox(self):
        if self._debug:
            print("mailbox()")

        return self._read_16(_RFD77402_MCPU_TO_HOST_MAILBOX)        

	# Tell MCPU to go to on state. Return true if successful
    def goto_on_mode(self):
        if self._debug:
            print("goto_on_mode()")

        # Set MCPU_ON
        self._write(_RFD77402_COMMAND, 0x92) # 0b.1001.0010 = Wake up MCPU to ON mode. Set valid command.

        # Check MCPU_ON Status
        for x in range(9):
            if (self._read_16(_RFD77402_DEVICE_STATUS) & 0x001F) == 0x0018: 
                return True # MCPU is now on
            time.sleep(0.01) # Suggested timeout for status checks from datasheet

        return False # Error - MCPU never turned on        

    # # Tell MCPU to go to off state. Return true if successful
    def goto_off_mode(self):
        if self._debug:
            print("goto_off_mode()")

        # Set MCPU_OFF
        self._write(_RFD77402_COMMAND, 0x91) # 0b.1001.0001 = Go MCPU off state. Set valid command.

        # Check MCPU_OFF Status
        for x in range(9):
            if (self._read_16(_RFD77402_DEVICE_STATUS) & 0x001F) == 0x0010:
                return True # MCPU is now off
            time.sleep(0.01) # Suggested timeout for status checks from datasheet

        return False # Error - MCPU never turned off

    # Tell MCPU to go to standby mode. Return true if successful
    def goto_standby_mode(self):
        if self._debug:
            print("goto_standby_mode()")
            
        #Set Low Power Standby
        self._write(_RFD77402_COMMAND, 0x90) # 0b.1001.0000 = Go to standby mode. Set valid command.

        # Check MCPU_ON Status
        for x in range(9):
            if (self._read_16(_RFD77402_DEVICE_STATUS) & 0x001F) == 0x0000:
                return True # MCPU is now in standby
                time.sleep(0.01) # Suggested timeout for status checks from datasheet
            else:
                return False # Error - MCPU never went to standby       

	# Tell MCPU to go to measurement mode. Takes a measurement. If measurement data is ready, return true
    def goto_measurement_mode(self):
        if self._debug:
            print("goto_measurement_mode()")

        # Single measure command
        self._write(_RFD77402_COMMAND, 0x81) # 0b.1000.0001 = Single measurement. Set valid command.

        # Read ICSR Register - Check to see if measurement data is ready
        for x in range(9):
            if (self._readRegister(_RFD77402_ICSR) & (1 << 4)) != 0: 
                return True # Data is ready!
            time.sleep(0.01) # Suggested timeout for status checks from datasheet
	    
        return False # Error - Timeout                 

	# Returns the chip ID. Should be 0xAD01 or higher.
    @property
    def chip_id(self):
        if self._debug:
            print("chip_id()")

        return self._read_16(_RFD77402_MOD_CHIP_ID)

    # Software reset the device
    def reset(self):
        if self._debug:
            print("reset()")

        self._write(_RFD77402_COMMAND, 1<<6)
        time.sleep(0.1)  

	# Retreive 2*27 bytes from MCPU for computation of calibration parameters
	# Reads 54 bytes into the calibration[] array
	# Returns true if new cal data is loaded
    @property
    def calibration_data(self):

        self._calibrationData[54]

        if not self._goto_on_mode():
            return False # Error - sensor timed out before getting to On Mode

        # Check ICSR Register and read Mailbox until it is empty
        messages = 0
        while (1):
            if ( (self._read(_RFD77402_ICSR) & (1 << 5)) == 0):
                break # Mailbox interrupt is cleared

            # Mailbox interrupt (Bit 5) is set so read the M2H mailbox register
            self.mailbox # Throw it out. Just read to clear the register.

            messages = messages + 1

            if messages > 27:
                return False # Error - Too many messages

            time.sleep(0.01) # Suggested timeout for status checks from datasheet

        # Issue mailbox command
        self.write_16(_RFD77402_HOST_TO_MCPU_MAILBOX, 0x0006) # Send 0x0006 mailbox command

        # Check to see if Mailbox can be read
        # Read 54 bytes of payload into the calibration[54] array
        for message in range(26):
            # Wait for bit to be set
            x = 0
            while 1:
                icsr = self.read(_RFD77402_ICSR)
                if ((icsr & (1 << 5)) != 0):
                    break # New message in available

                x = x + 1
                if x > 10:
                    return False #Error - Timeout

                time.sleep(0.01) # Suggested timeout for status checks from datasheet

            incoming = self.mailbox # Get 16-bit message

            # Put message into larger calibrationData array
            self._calibrationData[message * 2] = incoming >> 8
            self._calibrationData[message * 2 + 1] = incoming & 0xFF        

    # Reads two bytes from a given location from the RFD77402
    def _read_16(self, address):
        # Read and return a 16-bit unsigned big endian value read from the
        # specified 16-bit register address.
        if self._debug:
            print("_read_16()")
        with self._device:
            out_buffer = bytes([address])
            in_buffer = bytearray(2)
            self._device.write_then_readinto(out_buffer, in_buffer)
            if self._debug:
                print("$%02X => %s" % (address, [hex(i) for i in in_buffer]))
            return (in_buffer[1] << 8) | in_buffer[0]
	
    # Reads from a given location from the RFD77402
    def _read(self, address):
        # Read and return a byte from the specified 16-bit register address.
        if self._debug:
            print("_read()")
        with self._device:
            out_buffer = bytes([address])
            in_buffer = bytearray(1)
            self._device.write_then_readinto(out_buffer, in_buffer)
            if self._debug:
                print("$%02X => %s" % (address, [hex(i) for i in in_buffer]))
            return in_buffer[0]

	# Write a 16 bit value to a spot in the RFD77402
    def _write_16(self, address, data):
        # Write a 16-bit big endian value to the specified 16-bit register
        # address.
        if self._debug:
            print("_write_16()")
        with self._device:
            out_buffer = bytes([address, data & 0xFF, data >> 8])
            if self._debug:
                print("$%02X <= 0x%02X" % (address, data))
            self._device.write(out_buffer)

    # Write a value to a spot in the RFD77402
    def _write(self, address, data):
        # Write 1 byte of data from the specified 16-bit register address.\
        if self._debug:
            print("_write_16()")
        with self._device:
            out_buffer = bytes([address, data])
            if self._debug:
                print("$%02X <= 0x%02X" % (address, data))
            self._device.write(out_buffer)