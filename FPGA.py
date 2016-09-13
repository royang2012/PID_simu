import math

class PID:
    def __init__(self, sp, kp, ki, kd, pMax, intLimit):
        self.sp = sp
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.pMax = pMax
        self.integrator = 0
        self.kdTerReg = 0
        self.intLimit = intLimit
        self.dataIn = 0
        self.dataOut = 0
        self.error = 0
        self.kdTerDiff = 0
        self.kpTer = 0

    def ADCInput(self, ADCIn):
        self.dataIn = int(ADCIn)

    def DACOutput(self):
        return int(self.dataOut)

    def PIDComp(self):
        self.error = self.sp - self.dataIn
        self.kpTer = self.error * self.kp
        kiTer = self.error * self.ki
        self.integrator = self.integrator + kiTer
        if self.integrator > self.intLimit:
            self.integrator = self.intLimit
        elif self.integrator < -self.intLimit:
            self.integrator = -self.intLimit
        kdTer = self.error * self.kd
        self.kdTerDiff = kdTer - self.kdTerReg
        self.kdTerReg = kdTer
        pidSum = int((self.kpTer + self.integrator + self.kdTerDiff) / 8191)
        if pidSum > self.pMax:
            pidSum = self.pMax
        elif pidSum < 0:
            pidSum = 0
        self.dataOut = pidSum


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
