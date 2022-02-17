import time
import smbus2
import math

class Gyro:

    ### Essential register addresses ###
    CTRL_REG0 = 0x0D
    CTRL_REG1 = 0x13
    SLAVE_REG = 0x21
    STATUS_REG = 0x00

    ### Sensitivity values taken from datasheet table 35 ###
    SENSITIVITY_500DPS = 0.015625
    SENSITIVITY_1000DPS = 0.03125
    SENSITIVITY_2000DPS = 0.0625

    ### Range *TO BE TUNED* ###
    RANGE_500DPS = 17.45
    RANGE_1000DPS = 34.91
    RANGE_2000DPS = 69.82


    DPS_TO_RADIANS = 0.017453293

    ### Class members ###
    sensitivity = 0
    range = 0
    x = y = z = 0


    def __init__(self):
        with smbus2.SMBus(1) as bus:

            ### REGISTER SETUP ###
            bus.write_byte_data(Gyro.SLAVE_REG, Gyro.CTRL_REG1, 0x00) #set register to standby
            time.sleep(0.1)
            bus.write_byte_data(Gyro.SLAVE_REG, Gyro.CTRL_REG1, 0x40) #reset the register content
            time.sleep(0.1)
            bus.write_byte_data(Gyro.SLAVE_REG, Gyro.CTRL_REG0, 0x00) #reg sensitivity: 0x00 (2000dps) -> 0x02 (500dps)
            time.sleep(0.1)
            bus.write_byte_data(Gyro.SLAVE_REG, Gyro.CTRL_REG1, 0x0E) #set register to active
            time.sleep(0.1)
            
            ### SET DEFAULT RANGE AND SENSITIVITY TO 2000DPS ###
            self.sensitivity = Gyro.SENSITIVITY_2000DPS
            self.range = Gyro.RANGE_2000DPS


    def getAllAxes(self):
        with smbus2.SMBus(1) as bus:
            
            buffer = bus.read_i2c_block_data(Gyro.SLAVE_REG, Gyro.STATUS_REG, 7)
            raw_gyro_x = ((buffer[1] << 8) | buffer[2])
            raw_gyro_y = ((buffer[3] << 8) | buffer[4])
            raw_gyro_z = ((buffer[5] << 8) | buffer[6])

            self.x = raw_gyro_x * self.sensitivity * Gyro.DPS_TO_RADIANS
            self.y = raw_gyro_y * self.sensitivity * Gyro.DPS_TO_RADIANS
            self.z = raw_gyro_z * self.sensitivity * Gyro.DPS_TO_RADIANS

            if self.x > self.range:
                self.x = self.x - self.range
            if self.y > self.range:
                self.y = self.y - self.range
            if self.z > self.range:
                self.z = self.z - self.range
            
            #not sure if I should return something for this function
            return self.x, self.y, self.z


    def getResultantSpeed (self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


    def setSensitivity(self, _sensitivity):
        if (_sensitivity == 500):
            self.sensitivity = Gyro.SENSITIVITY_500DPS
            self.range = Gyro.RANGE_500DPS
        elif(_sensitivity == 1000):
            self.sensitivity = Gyro.SENSITIVITY_1000DPS
            self.range = Gyro.RANGE_1000DPS
        else: ### DEFAULT ###
            self.sensitivity = Gyro.SENSITIVITY_2000DPS
            self.range = Gyro.RANGE_2000DPS
        
