import time

# Data logging system to keep a short buffer of data points that can be saved on demand
# Keeps overall data storage low during any single use of the device


class Log:
    def __init__(self):
        self.buffer_length = 2500  # Number of data points stored
        self.buffers = [[[], []], [[], []], [[], []]]  # data for each sensor [[[data, ...],[time, ...]], ...]

        for buffer in range(len(self.buffers)):
            for i in range(self.buffer_length):  #
                self.buffers[buffer][0].append(0)
                self.buffers[buffer][1].append(0)

        self.buffer_i = [0, 0, 0]
        self.events = []
        self.event_i = 0  # Index of next event to be sent via MQTT
        self.sig_offsets = [1800, 1800]  # Removes DC offset read at the ADC
        self.sig_cal = [0, 0]  # Based upon the user's resting, balanced weight

        #  Timing data
        self.t_previous = time.perf_counter()
        self.t_cumulative = 0

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
        return d_sum / width

    def lpf_buffer(self, sig_id, width):  # Time averaging of defined width, entire buffer
        filtered_buffer = [[], []]
        for i in range(self.buffer_length):
            adjusted_width = width  # stop filter wrapping start and end of signal
            if i < width:
                adjusted_width = i + 1
            print(adjusted_width)
            filtered_buffer[0].append(self.lpf(sig_id, -i, adjusted_width))
            filtered_buffer[1].append(self.buffers[sig_id][1][self.i_convert(-i, self.buffer_i[sig_id] - 1)])
        return filtered_buffer  # new buffer, arranged in reverse time order

    def write(self, sig_id, d):  # Write a datapoint into a buffer and timestamp it
        self.buffers[sig_id][0][self.buffer_i[sig_id]] = d

        t = time.perf_counter()
        self.t_cumulative += t - self.t_previous
        self.t_previous = t

        self.buffers[sig_id][1][self.buffer_i[sig_id]] = time.time()
        self.buffer_i[sig_id] = self.i_wrap(self.buffer_i[sig_id])  # Increment buffer index

    def save_event(self):  # Formats the raw sensor data lpf -> offset -> calibration -> adjust timestamps to start at 0
        print("saving event")
        a0 = self.lpf_buffer(0, 10)
        a1 = self.lpf_buffer(1, 100)
        g0 = self.lpf_buffer(2, 3)
        for i in range(self.buffer_length):
            a0[0][i] = round((a0[0][i] - self.sig_offsets[0])/self.sig_cal[0] * 0.25, 4)
        for i in range(self.buffer_length):
            a1[0][i] = round((a1[0][i] - self.sig_offsets[1])/self.sig_cal[1] * 0.25, 4)
        self.events.append([a0, a1, g0])
        print("event appended")
        self.event_i += 1
