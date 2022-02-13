import time

# Data logging system to keep a short buffer of data points that can be saved on demand
# Keeps overall data storage low during any single use of the device


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