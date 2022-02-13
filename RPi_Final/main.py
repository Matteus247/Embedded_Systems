import smbus2
import time
import json
import paho.mqtt.client as mqtt
from Log import Log
from FsrAdc import FsrAdc
import concurrent.futures
from gpiozero import Button

log = Log()

adc0 = FsrAdc(0x48, 10)
adc1 = FsrAdc(0x49, 17)

t0 = time.process_time()

def readFsrAdcs():
    while (time.process_time() - t0 < 15):
        if not adc0.alert.is_held:
            log.write(0, adc0.read_conversion())
        if not adc1.alert.is_held:
            log.write(1, adc1.read_conversion())

def eventLogging():
    time.sleep(20)
    log.save_event()

    with open('data_out.txt', 'w') as f:  # Write out data
        for point in log.a_points[0]:
            f.write(str(point[0]) + ", " + str(point[1]))
            f.write('\n')
    with open('data_out1.txt', 'w') as f:
        for point in log.a_points[1]:
            f.write(str(point[0]) + ", " + str(point[1]))
            f.write('\n')
    with open('proc_out.txt', 'w') as f:
        for point in log.events[0][0]:
            f.write(str(point[0]) + ", " + str(point[1]))
            f.write('\n')
    with open('proc_out1.txt', 'w') as f:
        for point in log.events[0][1]:
            f.write(str(point[0]) + ", " + str(point[1]))
            f.write('\n')


if __name__ == '__main__':
    threads = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        print("Start threads")
        threads.append(executor.submit(readFsrAdcs))
        threads.append(executor.submit(eventLogging))
    print("End threads")
