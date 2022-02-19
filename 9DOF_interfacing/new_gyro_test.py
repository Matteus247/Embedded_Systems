import time
from Gyro import Gyro

gyro = Gyro()

while True:
    #gyro.getAllAxes()
    #print(gyro.x, "\t", gyro.y, "\t", gyro.z)
    
    print(gyro.getAllAxes(True)[0], "\t", gyro.getAllAxes(True)[1], "\t", gyro.getAllAxes(True)[2], "\t")
    print(gyro.getResultantSpeed(), "\n")
    
    time.sleep(0.2)

