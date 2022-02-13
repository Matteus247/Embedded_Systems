import smbus2
from gpiozero import Button


class FsrAdc:  # Manages i2c interaction with the external ADCs
    def __init__(self, address, alert_pin):  # Takes the i2c address of the ADC as hex
        self.acc = 0  # Accumulator for read block from ADC
        self.CONFIG_BLOCK = [0x42, 0xC4]
        self.config_is_setup = False
        self.address = address
        self.alert = Button(alert_pin)

        with smbus2.SMBus(1) as bus:  # Setup config registers
            if not self.config_is_setup:
                bus.write_i2c_block_data(self.address, 0x01, self.CONFIG_BLOCK)
                self.config_is_setup = True

    def read_conversion(self):  # Read conversion, return 16-bit integer
        with smbus2.SMBus(1) as bus:
            self.acc = bus.read_i2c_block_data(self.address, 0x00, 2)
        return self.acc[0] * 128 + self.acc[1]
