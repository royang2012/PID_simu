import math
import numpy as np

class PID:
    def __init__(self, sp_set, buffer_size):
        self.sp_set = sp_set
        # self.delay_time = delay_time
        self.s_in = 0
        self.p_in = 0
        self.u_out = 300
        self.out_buffer = np.ones(buffer_size)*300

    def ADC_input(self, ADC_in1, ADC_in2):
        self.s_in = int(ADC_in1)
        if self.s_in == 0:
            self.s_in = 1
        self.p_in = int(ADC_in2)
        if self.p_in == 0:
            self.p_in = 1

    def DAC_output(self):
        self.out_buffer[-1] = self.u_out
        self.out_buffer[0:-1] = self.out_buffer[1:]
        return int(self.out_buffer[0])

    def fb_comp(self):
        # if self.s_in >= 8100:
        #     self.u_out = np.sqrt(self.sp_set / self.s_in) * self.p_in / 4
        # else:
        #     self.u_out = np.sqrt(self.sp_set / self.s_in) * self.p_in / 2
        self.u_out = np.sqrt(self.sp_set / self.s_in) * self.p_in
        if self.u_out > 8191:
            self.u_out = 8191
        elif self.u_out < 100:
            self.u_out = 100



class LogComputation:
    def __init__(self):
        self.pIn = 0
        self.sIn = 0
        self.dataOut = 0
        self.logX_fpga = 0
        self.logX = 0

    def logAndSubtraction(self):
        if self.sIn == 0:
            self.sIn = 1
        if self.pIn == 0:
            self.pIn = 1
        logP = int(math.log10(float(self.pIn)) * 8191 / math.log10(8191))
        logS_2 = int(math.log10(self.sIn) * 8191 / math.log10(8191))/2
        self.logX_fpga = logS_2 - logP

    def DAAD(self):
        logX_analog = self.logX_fpga / 8191.0
        self.logX = int(logX_analog * 2048)
