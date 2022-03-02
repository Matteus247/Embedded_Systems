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

broker_ip = "146.169.153.141"

log = Log()

# Create sensor objects
gyro0 = Gyro()
adc0 = FsrAdc(0x48, 10)
adc1 = FsrAdc(0x49, 17)

t0 = time.perf_counter()

cal_button = Button(27)
red_led = LED(23)
green_led = LED(22)

# Setup MQTT connection
def on_disconnect(client, userdata, rc=0):
    client.loop_stop()

client = mqtt.Client()
print("created client")
print(client.connect(broker_ip, port=1883))
client.subscribe("IC.embedded/GROUP_NAME/#")
client.loop_start()
client.on_disconnect = on_disconnect


def readFsrAdcs():
    while True:
        if not adc0.alert.is_held:
            log.write(0, adc0.read_conversion())
        if not adc1.alert.is_held:
            log.write(1, adc1.read_conversion())


def readGyro():
    while True:
        gyro0.getAllAxes(True)
        out = gyro0.getResultantSpeed()
        log.write(2, out)
        time.sleep(0.01)


def eventLogging():
    red_led.on()
    green_led.off()
    cal_button.wait_for_active() # Wait for button press to start calibration
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
    print("Cals: ", fsr_0, " ", fsr_1) # Set ADC calibration values
    red_led.off()

    save_event = False
    while True:
        if save_event:
            green_led.on()
            log.save_event() # Save buffer data into an array of events for access
            print("writing event")

            # Create and send JSON object
            MQTT_dict = {
                "eventID": (log.event_i-1),
                "heel_data": log.events[log.event_i-1][0][0],
                "heel_time": log.events[log.event_i-1][0][1],
                "toe_data": log.events[log.event_i-1][1][0],
                "toe_time": log.events[log.event_i-1][1][1],
                "spin_data": log.events[log.event_i-1][2][0],
                "spin_time": log.events[log.event_i-1][2][1]
            }
            print("created dict")
            json_obj = json.dumps(MQTT_dict)
            print("created JSON")
            MSG_INFO = client.publish("IC.embedded/GROUP_NAME/test", json_obj)
            print(mqtt.error_string(MSG_INFO.rc))

            print("done writing")

            save_event = False
            green_led.off()
        else:
            green_led.blink(0.2, 0.2)
            cal_button.wait_for_active()
            save_event = True


if __name__ == '__main__':
    threads = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print("Start threads")
        threads.append(executor.submit(readFsrAdcs))
        threads.append(executor.submit(eventLogging))
        threads.append(executor.submit(readGyro))
    print("End threads")
