import time
import smbus2

bus = smbus2.SMBus(1)

read_result= smbus2.i2c_msg.read(0x1E,2)
bus.i2c_rdwr(read_result)

'''
#read = smbus2.i2c_msg.read(80,64)

for i in range(1, 100):
    read_data = smbus2.i2c_msg.read(80, 2)
    bus.i2c_rdwr(read_data)
    print(read_data)
    time.sleep(100)
'''