
import board
import busio
import sparkfun_rfd77402
from sparkfun_rfd77402 import RFD77402_ADDR

i2c = busio.I2C(sda=board.IO8, scl=board.IO9)

proximity_bus = sparkfun_rfd77402.rfd77402(i2c=i2c, address=RFD77402_ADDR, debug=True)

result = proximity_bus.begin()

print(result)