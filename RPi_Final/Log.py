import time

# Data logging system to keep a short buffer of data points that can be saved on demand
# Keeps overall data storage low during any single use of the device


class Log:
    def __init__(self):
        self.buffer_length = 5000  # Number of data points stored
        self.buffers = [[[], []], [[], []]]  # data for each sensor [[[data, ...],[time, ...]], ...]
        for i in range(self.buffer_length):  #
            self.buffers[0][0].append(0)
            self.buffers[0][1].append(0)
            self.buffers[1][0].append(0)
            self.buffers[1][1].append(0)
        self.buffer_i = [0, 0]
        self.events = []
        self.event_i = 0  # Index of next event to be sent via MQTT
        self.sig_offsets = [1430, 1430]  # Removes DC offset read at the ADC
        self.sig_cal = [0, 0]  # Based upon the user's resting, balanced weight

    def i_wrap(self, i):
        if i < (self.buffer_length - 1):
            return i + 1
        else:
            return 0

    def i_convert(self, i_relative, i_current):  # Maps relative index to current index in a buffer
        i = i_current + i_relative
        if i > self.buffer_length - 1:
            return i - self.buffer_length
        elif i < 0:
            return self.buffer_length + i
        else:
            return i

    def lpf(self, sig_id, index, width):  # Time averaging of defined width, at a single index
        d_sum = 0
        for c in range(width):
            d_sum += self.buffers[sig_id][0][self.i_convert(index + c - width + 1, self.buffer_i[sig_id])]
        return int(d_sum / width)

    def rolling_lpf(self, sig_id, width):
        return 0

    def lpf_buffer(self, sig_id, width):  # Time averaging of defined width, entire buffer
        filtered_buffer = [[], []]
        for i in range(self.buffer_length):
            filtered_buffer[0].append(self.lpf(sig_id, -i, width))
            filtered_buffer[1].append(self.buffers[sig_id][1][self.i_convert(-i, self.buffer_i[sig_id] - 1)])
        return filtered_buffer  # new buffer, arranged in time order

    def write(self, sig_id, d):  # Write a datapoint into a buffer and timestamp it
        self.buffers[sig_id][0][self.buffer_i[sig_id]] = d
        self.buffers[sig_id][1][self.buffer_i[sig_id]] = time.process_time()
        self.buffer_i[sig_id] = self.i_wrap(self.buffer_i[sig_id])  # Increment buffer index

    def save_event(self):  # Formats the raw sensor data lpf -> offset -> calibration -> adjust timestamps to start at 0
        print("saving event")
        a0 = self.lpf_buffer(0, 5)
        #print(a0)
        a1 = self.lpf_buffer(1, 10)
        t_off0 = a0[1][self.buffer_length - 1]
        t_off1 = a1[1][0]
        for i in range(self.buffer_length):
            a0[0][i] = a0[0][i] - self.sig_offsets[0]
            a0[1][i] = round(a0[1][i] - t_off0, 4)  # Set the time of the event to start from 0
        for i in range(self.buffer_length):
            a1[0][1] = a1[0][i] - self.sig_offsets[1]
            a1[1][i] = round(a1[1][i] - t_off1, 4)
        self.events.append([a0, a1])
