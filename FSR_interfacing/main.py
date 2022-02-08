import smbus2
import time
from gpiozero import Button


class Log:
    def __init__(self):
        self.buffer_length = 5000
        self.a_points = [[], []]
        for i in range(self.buffer_length):
            self.a_points[0].append([0, 0])
            self.a_points[1].append([0, 0])
        self.a_i = [0, 0]
        self.events = []
        self.a_offsets = [1450, 1450]
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
        if i > 4999:
            return i - 5000
        else:
            return i

    def lpf(self, sig_id, width):  # Time averaging of defined width
        out = []
        for i in range(len(self.a_points[sig_id])):
            d_sum = 0
            for c in range(width):
                d_sum += self.a_points[sig_id][self.i_convert(i + c - width + 1, self.a_i[sig_id])][0]
            t_avg = d_sum/4
            out.append([t_avg, self.a_points[sig_id][self.i_convert(i, self.a_i[sig_id])][1]])
        return out

    def write(self, sig_id, d):
        a = [d, time.process_time()]
        self.a_points[sig_id][self.a_i[sig_id]] = a
        self.a_i[sig_id] = self.i_wrap(self.a_i[sig_id])

    def save_event(self):
        a0 = self.lpf(0, 4)
        a1 = self.lpf(1, 4)
        for i in range(len(a1)):
            a1[i][0] = a1[i][0] - self.a_offsets[1]
        for i in range(len(a0)):
            a1[i][0] = a1[i][0] - self.a_offsets[1]
        self.events.append([a0, a1])


log = Log()

config_block = [0x42, 0x84]  # Set continuous conversion a0 128SPS with alert active low

alert0 = Button(10)  # Alert pin is active low
alert1 = Button(17)

t0 = time.process_time()

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
            f.write(str(point[0]))
            f.write('\n')
