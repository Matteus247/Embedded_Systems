import time
import smbus2
import matplotlib

#bus = smbus2.SMBus(1)
#time.sleep(1)

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

with smbus2.SMBus(1) as bus:
    '''
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
    '''
    #test_data =
    bus.write_byte_data(0x1F, 0x2A, 0x00)
    time.sleep(0.1)
    bus.write_byte_data(0x1F, 0x5B, 0x1F)
    time.sleep(0.1)
    bus.write_byte_data(0x1F, 0x5C, 0x20)
    time.sleep(0.1)
    bus.write_byte_data(0x1F, 0x0E, 0x01)
    time.sleep(0.1)
    bus.write_byte_data(0x1F, 0x2A, 0x0D)
    time.sleep(0.1)
    


    while True:
        #acc3 = bus.read_i2c_block_data(0x1F, 0x00, 30) #reading from slave_addr, with status_offset, 30 bytes
        Buffer = bus.read_i2c_block_data(0x1F, 0x00, 13)
        #print(acc3[1], acc3[3], acc3[5])
        accel_x =((Buffer[1] << 8) | Buffer[2])>> 2
        accel_y = ((Buffer[3] << 8) | Buffer[4])>> 2
        accel_z = ((Buffer[5] << 8) | Buffer[6])>> 2
        print(accel_x)
        print(accel_y)
        print(accel_z)
        '''
        mag_x = (Buffer[7] << 8) | Buffer[8];
        print(mag_x)
        print(2|3)
        '''
        '''
        print(((Buffer[1] << 8) | Buffer[2])>> 2)
        print(((Buffer[3] << 8) | Buffer[4])>> 2)
        print(((Buffer[5] << 8) | Buffer[6])>> 2)
        '''
        #print(1 << 4)
        #print(acc3)
        print()
        time.sleep(0.5)
        

#copy the 14 bit accelerometer byte data into 16 bit words


'''
#read = smbus2.i2c_msg.read(80,64)

for i in range(1, 100):
    read_data = smbus2.i2c_msg.read(80, 2)
    bus.i2c_rdwr(read_data)
    print(read_data)
    time.sleep(100)
'''