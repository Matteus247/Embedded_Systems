import smbus2
import time
import json
import paho.mqtt.client as mqtt
from Log import Log
from FsrAdc import FsrAdc
from Gyro import Gyro
import concurrent.futures
from gpiozero import Button
from gpiozero import LED

log = Log()

gyro0 = Gyro()
adc0 = FsrAdc(0x48, 10)
adc1 = FsrAdc(0x49, 17)

t0 = time.perf_counter()

cal_button = Button(27)
red_led = LED(23)
green_led = LED(22)


def readFsrAdcs():
    while (time.perf_counter() - t0 < 30):
        if not adc0.alert.is_held:
            log.write(0, adc0.read_conversion())
        if not adc1.alert.is_held:
            log.write(1, adc1.read_conversion())


def readGyro():
    while (time.perf_counter() - t0 < 30):
        gyro0.getAllAxes(True)
        out = gyro0.getResultantSpeed()
        log.write(2, out)
        print(out)
        time.sleep(0.01)


def eventLogging():
    red_led.on()
    green_led.off()
    cal_button.wait_for_active()
    red_led.blink(0.1, 0.1)
    time.sleep(0.2)  # Do calibration here

    t_err = time.perf_counter()  # Tracks last time a signal moved by more than 10%
    fsr_0 = 0
    fsr_1 = 0
    while time.perf_counter() - t_err < 3:  # Wait for signal to remain within +-10% band for 1 second
        fsr_0pp = log.lpf(0, 0, 15)
        fsr_1pp = log.lpf(1, 0, 25)
        if fsr_0pp > fsr_0*1.1 or fsr_0pp < fsr_0*0.9:
            t_err = time.perf_counter()
        elif fsr_1pp > fsr_1*1.1 or fsr_1pp < fsr_1*0.9:
            t_err = time.perf_counter()
        fsr_0 = fsr_0pp
        fsr_1 = fsr_1pp
    log.sig_cal[0] = fsr_0 - log.sig_offsets[0]
    log.sig_cal[1] = fsr_1 - log.sig_offsets[1]
    print("Cals: ", fsr_0, " ", fsr_1)
    red_led.off()

    #cal_button.wait_for_active()
    time.sleep(10)
    green_led.blink(0.1, 0.1)
    time.sleep(5)
    green_led.on()
    log.save_event()

    with open('proc_out.txt', 'w') as f:
        for i in range(2500):
            f.write(str(log.events[0][0][0][i]) + ", " + str(log.events[0][0][1][i]))
            f.write('\n')

    with open('proc_out1.txt', 'w') as f:
        for i in range(2500):
            f.write(str(log.events[0][1][0][i]) + ", " + str(log.events[0][1][1][i]))
            f.write('\n')

    with open('proc_out2.txt', 'w') as f:
        for i in range(2500):
            f.write(str(log.events[0][2][0][i]) + ", " + str(log.events[0][2][1][i]))
            f.write('\n')


if __name__ == '__main__':
    threads = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print("Start threads")
        threads.append(executor.submit(readFsrAdcs))
        threads.append(executor.submit(eventLogging))
        threads.append(executor.submit(readGyro))
    print("End threads")
