import time
import smbus2
#import matplotlib

##write 0000 0000 = 0x00 to accelerometer control register 1 to place FXOS8700CQ into standby (CTRL_REG_1)
##write 0001 1111 = 0x1F to magnetometer control register 1 (M_CTRL_REG_1)
##write 0010 0000 = 0x20 to magnetometer control register 2 (M_CTRL_REG_2)
##write 0000 0001= 0x01 to XYZ_DATA_CFG register
##write 0000 1101 = 0x0D to accelerometer control register 1 (CTRL_REG_1)
FXOS8700CQ_XYZ_DATA_CFG = 0x0E
FXOS8700CQ_CTRL_REG1    = 0x2A
FXOS8700CQ_M_CTRL_REG1  = 0x5B
FXOS8700CQ_M_CTRL_REG2  = 0x5C
ACCEL_MG_LSB_2G = 0.000244
ACCEL_MG_LSB_4G = 0.000488
ACCEL_MG_LSB_8G = 0.000976
SENSORS_GRAVITY_STANDARD = 9.80#665

with smbus2.SMBus(1) as bus:
    
    ### SETUP ###
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
        Buffer = bus.read_i2c_block_data(0x1F, 0x00, 13)
        raw_accel_x = ((Buffer[1] << 8) | Buffer[2])>> 2
        raw_accel_y = ((Buffer[3] << 8) | Buffer[4])>> 2
        raw_accel_z = ((Buffer[5] << 8) | Buffer[6])>> 2
        
        accel_x = raw_accel_x * ACCEL_MG_LSB_4G * SENSORS_GRAVITY_STANDARD 
        accel_y = raw_accel_y * ACCEL_MG_LSB_4G * SENSORS_GRAVITY_STANDARD 
        accel_z = raw_accel_z * ACCEL_MG_LSB_4G * SENSORS_GRAVITY_STANDARD
        
        if accel_x > 39.2:
            accel_x = accel_x - 78.4
        
        if accel_y > 39.2:
            accel_y = accel_y - 78.4
            
        if accel_z > 39.2:
            accel_z = accel_z - 78.4
        '''
        print(Buffer[1] , ' ' , Buffer[2] , "=>" , raw_accel_x, "=>", accel_x)
        print(Buffer[3] , ' ' , Buffer[4] , "=>" , raw_accel_y, "=>", accel_y)
        print(Buffer[5] , ' ' , Buffer[6] , "=>" , raw_accel_z, "=>", accel_z)
        '''
        print("X: ", accel_x, "\tY: ", accel_y, "\tZ: ", accel_z)
        print()
        time.sleep(0.6)
        