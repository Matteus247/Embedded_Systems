import smbus2
import time
import json
from gpiozero import Button


class Log:
    def __init__(self):
        self.buffer_length = 5000  # Number of data points stored
        self.a_points = [[], []]  # Sets of data points for each sensor
        for i in range(self.buffer_length):  #
            self.a_points[0].append([0, 0])
            self.a_points[1].append([0, 0])
        self.a_i = [0, 0]
        self.events = []
        self.event_i = 0  # Index of next event to be sent via MQTT
        self.a_offsets = [1430, 1430]
        self.a_cal = [0, 0]

    def i_wrap(self, i):
        if i < (self.buffer_length - 1):
            return i + 1
        else:
            return 0

    def i_convert(self, i_relative, i_current):  # Maps relative index to current index in a buffer
        if i_relative < 0:  # Useful when applying lpf to not wrap the filter
            return i_current
        i = i_current + i_relative
        if i > self.buffer_length - 1:
            return i - self.buffer_length
        else:
            return i

    def lpf(self, sig_id, width):  # Time averaging of defined width
        out = []
        for i in range(len(self.a_points[sig_id])):
            d_sum = 0
            for c in range(width):
                d_sum += self.a_points[sig_id][self.i_convert(i + c - width + 1, self.a_i[sig_id])][0]
            t_avg = int(d_sum/width)
            out.append([t_avg, self.a_points[sig_id][self.i_convert(i, self.a_i[sig_id])][1]])
        return out

    def write(self, sig_id, d):  # Write a datapoint into a buffer and timestamp it
        self.a_points[sig_id][self.a_i[sig_id]] = [d, time.process_time()]
        self.a_i[sig_id] = self.i_wrap(self.a_i[sig_id])

    def save_event(self):  # Formats the raw sensor data lpf -> offset -> calibration -> adjust timestamps to start at 0
        a0 = self.lpf(0, 4)
        a1 = self.lpf(1, 10)
        t_off0 = a0[0][1]
        t_off1 = a1[0][1]
        for i in range(len(a0)):
            a0[i][0] = a0[i][0] - self.a_offsets[0]
            a0[i][1] = round(a0[i][1] - t_off0, 4)  # Set the time of the event to start from 0
        for i in range(len(a1)):
            a1[i][0] = a1[i][0] - self.a_offsets[1]
            a1[i][1] = round(a1[i][1] - t_off1, 4)
        self.events.append([a0, a1])


log = Log()

config_block = [0x42, 0x84]  # Set continuous conversion a0 128SPS with alert active low

alert0 = Button(10)  # Alert pin is active low
alert1 = Button(17)

t0 = time.process_time()

dicMes = {}

if __name__ == '__main__':
    with smbus2.SMBus(1) as bus:
        bus.write_i2c_block_data(0x48, 0x01, config_block)
        bus.write_i2c_block_data(0x49, 0x01, config_block)
        while (time.process_time() - t0) < 10:
            if not alert0.is_held:
                acc = bus.read_i2c_block_data(0x48, 0x00, 2)
                log.write(0, acc[0] * 128 + acc[1])
            if not alert1.is_held:
                acc = bus.read_i2c_block_data(0x49, 0x00, 2)
                log.write(1, acc[0] * 128 + acc[1])

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

    # data = [0, log.events[0][0], log.events[0][1]]
    # son_object = json.dumps(data)
    # print(json_object)
    print("version2")
    sensorReading = {
        "eventId": 0,
        "signalOne": log.events[0][0],
        "signalTwo": log.events[0][1]
    }

    json_object = json.dumps(sensorReading)
    print(json_object)