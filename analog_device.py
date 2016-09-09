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

    def __init__(self, delayTime, bandWidth):
        self.delayTime = delayTime
        self.bandWidth = bandWidth
        self.dataIn = np.zeros(vectorLength)
        self.compResult = 0
        self.dataOut = np.zeros(vectorLength)
        self.timeConst = sampleFreq/bandWidth

    def deviceIni(self, inputVector, outputVector):
        self.dataIn = inputVector
        self.dataOut = outputVector

    def outputComp(self):
        self.dataOut[0:vectorLength-2] = self.dataOut[1:vectorLength-1]
        self.dataOut[-1] = lowpass(self.dataOut[vectorLength-2], self.compResult, self.timeConst)

    @abstractmethod
    def processComp(self, delayTime): pass

class LowPassFilter(AnalogDevice):

    def processComp(self, delayTime):
        self.compResult = self.dataIn[vectorLength-delayTime-1]


