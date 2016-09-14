import math

class PID:
    def __init__(self, sp_set, kp_set, ki_set, kd_set, pMax_set, intLimit_set):
        self.sp_set = sp_set
        self.kp_set = kp_set
        self.ki_set = ki_set
        self.kd_set = kd_set
        self.pMax_set = pMax_set
        self.integrator = 0
        self.kdTerReg = 0
        self.intLimit_set = intLimit_set
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
        sp = self.sp_set
        self.error = sp - self.dataIn
        pMax = self.pMax_set

        if (self.integrator >= 0.3 * self.intLimit_set):
            if(self.dataIn > 3000):
                ki = self.ki_set
                kp = self.kp_set
            else:
                ki = 0.2 * self.ki_set
                kp = 0.5 * self.kp_set
        elif self.dataIn > 0.2 * sp:
            if self.dataOut < 0.5 * pMax:
                ki = 0.05 * self.ki_set
                kp = 0.2 * self.kp_set
            else:
                ki = 0.1 * self.ki_set
                kp = 0.4 * self.kp_set
        else:
            ki = 0.2 * self.ki_set
            kp = 0.5 * self.kp_set
        kd = self.kd_set

        intLimit = self.intLimit_set
        self.error = sp - self.dataIn
        self.kpTer = self.error * kp
        kiTer = self.error * ki
        self.integrator = self.integrator + kiTer
        if self.integrator > intLimit:
            self.integrator = intLimit
        elif self.integrator < -intLimit:
            self.integrator = -intLimit
        kdTer = self.error * kd
        self.kdTerDiff = kdTer - self.kdTerReg
        self.kdTerReg = kdTer
        pidSum = int((self.kpTer + self.integrator + self.kdTerDiff) / 4096)
        if pidSum > pMax:
            pidSum = pMax
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
