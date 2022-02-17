import time
from Gyro import Gyro

gyro = Gyro()

while True:
    gyro.getAllAxes()
    print(gyro.x, "\t", gyro.y, "\t", gyro.z, "\n")
    time.sleep(0.3)

