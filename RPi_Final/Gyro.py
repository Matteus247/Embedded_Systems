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
    RANGE_2000DPS = 69.95


    DPS_TO_RADIANS = 0.017453293

    ### Class members ###
    sensitivity = 0
    filtered = True
    range = 0
    x = y = z = 0


    def __init__(self):
        with smbus2.SMBus(1) as bus:

            ### REGISTER SETUP ###
            bus.write_byte_data(self.SLAVE_REG, self.CTRL_REG0, 0x00) #reg sensitivity: 0x00 (2000dps) -> 0x02 (500dps)
            time.sleep(0.1)
            bus.write_byte_data(self.SLAVE_REG, self.CTRL_REG1, 0x0E) #set register to active
            time.sleep(0.1)
            
            ### SET DEFAULT RANGE AND SENSITIVITY TO 2000DPS ###
            self.sensitivity = Gyro.SENSITIVITY_2000DPS
            self.range = Gyro.RANGE_2000DPS


    def getAllAxes(self, filtered:bool):
        with smbus2.SMBus(1) as bus:
            
            buffer = bus.read_i2c_block_data(self.SLAVE_REG, self.STATUS_REG, 7)
            raw_gyro_x = ((buffer[1] << 8) | buffer[2])
            raw_gyro_y = ((buffer[3] << 8) | buffer[4])
            raw_gyro_z = ((buffer[5] << 8) | buffer[6])

            self.x = raw_gyro_x * self.sensitivity * self.DPS_TO_RADIANS
            self.y = raw_gyro_y * self.sensitivity * self.DPS_TO_RADIANS
            self.z = raw_gyro_z * self.sensitivity * self.DPS_TO_RADIANS

            ### Wrap values to be symmetric around 0 ###
            if self.x > self.range / 2:
                self.x = self.x - self.range
            if self.y > self.range / 2:
                self.y = self.y - self.range
            if self.z > self.range / 2:
                self.z = self.z - self.range
            
            ### Filter values, needed due to some unidentified jumps in readings ###
            if self.filtered == True:
                if abs(self.x) < 2:
                    self.x = 0
                if abs(self.y) < 2:
                    self.y = 0
                if abs(self.z) < 2:
                    self.z = 0
            
            return round(self.x, 3), round(self.y, 3), round(self.z, 3)


    def getResultantSpeed (self):
        return round(math.sqrt(round(self.x, 3) ** 2 + round(self.y, 3) ** 2 + round(self.z, 3) ** 2), 3)
    
    
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
        
