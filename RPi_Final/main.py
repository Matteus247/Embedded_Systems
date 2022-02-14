import smbus2
import time
import json
import paho.mqtt.client as mqtt
from Log import Log
from FsrAdc import FsrAdc
import concurrent.futures
from gpiozero import Button
from gpiozero import LED

log = Log()

adc0 = FsrAdc(0x48, 10)
adc1 = FsrAdc(0x49, 17)

t0 = time.process_time()

cal_button = Button(27)
red_led = LED(23)
green_led = LED(22)


def readFsrAdcs():
    while (time.process_time() - t0 < 20):
        if not adc0.alert.is_held:
            log.write(0, adc0.read_conversion())
        if not adc1.alert.is_held:
            log.write(1, adc1.read_conversion())


def eventLogging():
    red_led.on()
    green_led.off()
    cal_button.wait_for_active()
    red_led.blink(0.1, 0.1)
    green_led.on()

    time.sleep(15)
    log.save_event()

    with open('proc_out.txt', 'w') as f:
        for i in range(5000):
            f.write(str(log.events[0][0][0][i]) + ", " + str(log.events[0][0][1][i]))
            f.write('\n')

if __name__ == '__main__':
    threads = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        print("Start threads")
        threads.append(executor.submit(readFsrAdcs))
        threads.append(executor.submit(eventLogging))
    print("End threads")
