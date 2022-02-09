import time
import smbus2

bus = smbus2.SMBus(1)
time.sleep(1)

##write 0000 0000 = 0x00 to accelerometer control register 1 to place FXOS8700CQ into standby (CTRL_REG_1)
##write 0001 1111 = 0x1F to magnetometer control register 1 (M_CTRL_REG_1)
##write 0010 0000 = 0x20 to magnetometer control register 2 (M_CTRL_REG_2)
##write 0000 0001= 0x01 to XYZ_DATA_CFG register
##write 0000 1101 = 0x0D to accelerometer control register 1 (CTRL_REG_1)

#define FXOS8700CQ_XYZ_DATA_CFG   0x0E
#define FXOS8700CQ_CTRL_REG1      0x2A
#define FXOS8700CQ_M_CTRL_REG1    0x5B
#define FXOS8700CQ_M_CTRL_REG2    0x5C

FXOS8700CQ_XYZ_DATA_CFG = 0x0E
FXOS8700CQ_CTRL_REG1    = 0x2A
FXOS8700CQ_M_CTRL_REG1  = 0x5B
FXOS8700CQ_M_CTRL_REG2  = 0x5C

first = smbus2.i2c_msg.write(FXOS8700CQ_CTRL_REG1, 0x00)
second = smbus2.i2c_msg.write(FXOS8700CQ_M_CTRL_REG1, 0x1F)
third = smbus2.i2c_msg.write(FXOS8700CQ_M_CTRL_REG2, 0x20)
fourth = smbus2.i2c_msg.write(FXOS8700CQ_XYZ_DATA_CFG, 0x01)
fifth = smbus2.i2c_msg.write(FXOS8700CQ_CTRL_REG1, 0x0D)

bus.i2c_rdwr(first)
time.sleep(1)
bus.i2c_rdwr(second)
time.sleep(1)
bus.i2c_rdwr(third)
time.sleep(1)
bus.i2c_rdwr(fourth)
time.sleep(1)
bus.i2c_rdwr(fifth)
time.sleep(1)





read_result= smbus2.i2c_msg.read(0x1E,13)
reading = bus.i2c_rdwr(read_result)
time.sleep(1)
print(reading)

#copy the 14 bit accelerometer byte data into 16 bit words


'''
#read = smbus2.i2c_msg.read(80,64)

for i in range(1, 100):
    read_data = smbus2.i2c_msg.read(80, 2)
    bus.i2c_rdwr(read_data)
    print(read_data)
    time.sleep(100)
'''