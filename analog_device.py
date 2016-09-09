import numpy as np
from abc import ABCMeta, abstractmethod

def lowpass(memory, input, timeConst):
    return memory/timeConst*(timeConst-1) + input/timeConst


class AnalogDevice:
    __metaclass__ = ABCMeta
    global timeResolution #us
    timeResolution = 0.1
    global sampleFreq #us
    sampleFreq = 1/timeResolution
    global vectorLength
    vectorLength = 50

    def __init__(self, delayTime, bandWidth, gain):
        self.delayTime = delayTime
        self.bandWidth = bandWidth
        self.dataIn = np.zeros(vectorLength)
        self.compResult = 0
        self.dataOut = np.zeros(vectorLength)
        if sampleFreq <= bandWidth:
            self.timeConst = 1
        else:
            self.timeConst = sampleFreq / bandWidth
        self.gain = gain

    def deviceIni(self, inputVector, outputVector):
        self.dataIn = inputVector
        self.dataOut = outputVector

    def outputComp(self):
        self.dataOut[0:vectorLength-1] = self.dataOut[1:vectorLength]
        self.dataOut[-1] = lowpass(self.dataOut[vectorLength-1], self.compResult, self.timeConst)

    @abstractmethod
    def processComp(self, delayTime, input2): pass


class LowPassFilter(AnalogDevice):
    def processComp(self, delayTime, input2=0):
        self.compResult = self.dataIn[vectorLength - delayTime*sampleFreq - 1]


class Microscopy(AnalogDevice):
    def processComp(self, delayTime, input2):
        self.compResult = self.gain * input2 *\
                          self.dataIn[vectorLength - delayTime*sampleFreq - 1] ^ 2

class EOM(AnalogDevice):
    def __init__(self, delayTime, bandWidth, gain, minOut, maxOut):
        AnalogDevice.__init__(self, delayTime, bandWidth, gain)
        self.minOut = minOut
        self.maxOut = maxOut

    def processComp(self, delayTime, input2):
        tempOut = self.gain * input2 * \
                          self.dataIn[vectorLength - delayTime * sampleFreq - 1]
        if tempOut >= self.minOut & tempOut <= self.maxOut:
            self.compResult = tempOut
        elif tempOut <= self.minOut:
            self.compResult = self.minOut
        else:
            self.compResult = self.maxOut
