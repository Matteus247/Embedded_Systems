import time
import smbus2



GYRO_REGISTER_CTRL_REG0 = 0x0D #, /**< 0x0D (default value = 0b00000000, read/write) */
GYRO_REGISTER_CTRL_REG1 = 0x13 #, /**< 0x13 (default value = 0b00000000, read/write) */
GYRO_REGISTER_CTRL_REG2 = 0x14 #, /**< 0x14 (default value = 0b00000000, read/write) */
GYRO_REGISTER_SLAVE_REG = 0x21
GYRO_REGISTER_STATUS = 0x00

GYRO_RANGE_250DPS = 250 #,   /**< 250dps */
GYRO_RANGE_500DPS = 500 #,   /**< 500dps */

GYRO_SENSITIVITY_250DPS = 0.0078125 #lower dynamic range -> slow rotations
GYRO_SENSITIVITY_500DPS = 0.015625 
GYRO_SENSITIVITY_1000DPS= 0.03125 #broader dynamic range -> fast rotations
GYRO_SENSITIVITY_2000DPS= 0.0625
GYRO_DPS_TO_RADS = 0.017453293

with smbus2.SMBus(1) as bus:
	
	### SETUP ###
    bus.write_byte_data(0x21, 0x13, 0x00)
    time.sleep(0.1)
    #bus.write_byte_data(0x21, 0x13, 0x40)
    time.sleep(0.1)
    bus.write_byte_data(0x21, 0x0D, 0x02) #change gyro sensitivity
    time.sleep(0.1)
    bus.write_byte_data(0x21, 0x13, 0x0E)
    time.sleep(0.1)
    
    
    #bus.write_byte_data(0x1F, 0x2A, 0x0D)
    #time.sleep(0.1)
    
    max_x = 0
    min_x = 50
    max_y = 0
    max_z = 0
    min_z = 50
    
    readings = open("readings_z_axis.txt", "w")
    readings.write("line\n")
    i = 0 
    while i < 100:
        Buffer = bus.read_i2c_block_data(0x21, 0x00, 7)
        raw_gyro_x = ((Buffer[1] << 8) | Buffer[2])
        raw_gyro_y = ((Buffer[3] << 8) | Buffer[4])
        raw_gyro_z = ((Buffer[5] << 8) | Buffer[6])
        
        gyro_x = raw_gyro_x * GYRO_SENSITIVITY_1000DPS * GYRO_DPS_TO_RADS
        gyro_y = raw_gyro_y * GYRO_SENSITIVITY_1000DPS * GYRO_DPS_TO_RADS
        gyro_z = raw_gyro_z * GYRO_SENSITIVITY_1000DPS * GYRO_DPS_TO_RADS
        
        #implement wrap around
        '''
        if gyro_x > max_x:
            max_x = gyro_x
        if gyro_y > max_y:
            max_y = gyro_y
        if gyro_z > max_z:
            max_z = gyro_z
        '''
        
        '''   
        if gyro_x > 4.467: #FOR 250 DPS
            gyro_x = gyro_x - 8.9359
        if gyro_y > 4.467:
            gyro_y = gyro_y - 8.9359
        if gyro_z > 4.467:
            gyro_z = gyro_z - 8.9359
        '''
        
        if gyro_x > 17.872: #FOR 1000 DPS
            gyro_x = gyro_x - 35.7436
        if gyro_y > 17.872:
            gyro_y = gyro_y - 35.7436
        if gyro_z > 17.872:
            gyro_z = gyro_z - 35.7436       
        #max is 8.93595 for 250 DPS
        #max is 35.7436 for 1000 DPS
            
        #fine calibration TBD, need an Arduino for reference
        if gyro_x > max_x:
            max_x = gyro_x
        if gyro_y > max_y:
            max_y = gyro_y
        if gyro_z > max_z:
            max_z = gyro_z
        if gyro_x < min_x:
            min_x = gyro_x
        if gyro_z < min_z:
            min_z = gyro_z
        
        print("X: ", gyro_x, "\tY: ", gyro_y, "\tZ: ", gyro_z)
        
        #print(min_x, "\t", max_x)
        print(min_z, "\t", max_z)
        secs = time.time()
        
        readings.write(str(gyro_z))
        readings.write(",")
        readings.write(str(secs))
        readings.write("\n")
        '''
        readings.write(str(max_z))
        readings.write("\n")'''
        
        '''
        print(max_x)
        print(max_y)
        print(max_z)
        '''
        
        print()
        i = i + 1
        time.sleep(0.3)
            
    
    readings.close()