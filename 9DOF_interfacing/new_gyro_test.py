import time
from Gyro import Gyro

gyro = Gyro()

while True:
    #gyro.getAllAxes()
    #print(gyro.x, "\t", gyro.y, "\t", gyro.z)
    
    print(gyro.getAllAxes()[0], "\t", gyro.getAllAxes()[1], "\t", gyro.getAllAxes()[2], "\t")
    print(gyro.getResultantSpeed(), "\n")
    
    time.sleep(0.2)

