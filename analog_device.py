import numpy as np
from abc import ABCMeta, abstractmethod
from scipy.signal import butter, lfilter, freqz

# def lowpass(memory, input, timeConst):
#     return memory/timeConst*(timeConst-1) + input/timeConst
def butter_lowpass(cutoff, fs, order=3):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

class AnalogDevice:
    __metaclass__ = ABCMeta
    global timeResolution #us
    timeResolution = 0.008
    global sampleFreq #us
    sampleFreq = 1/timeResolution
    global vectorLength
    vectorLength = 500 # 4us, pixel time

    def __init__(self, delayTime, bandWidth, gain):
        self.delayTime = float(delayTime)
        self.bandWidth = float(bandWidth)
        self.unfDataOut = np.zeros(vectorLength)
        self.dataIn = np.zeros(vectorLength)
        self.compResult = 0
        self.dataOut = np.zeros(vectorLength)
        if sampleFreq <= bandWidth:
            self.timeConst = 1
        else:
            self.timeConst = sampleFreq / bandWidth
        self.gain = float(gain)
        if self.bandWidth <= sampleFreq/2:
            b, a = butter(4, 2/self.timeConst, btype='low', analog=False)
            self.lowPassB = b
            self.lowPassA = a


    def deviceIni(self, inputVector, outputVector):
        self.dataIn = inputVector
        self.dataOut = outputVector

    def outputComp(self):
        self.unfDataOut[0:-1] = self.unfDataOut[1:]
        self.unfDataOut[-1] = self.compResult
        if self.bandWidth <= sampleFreq/2:
            self.dataOut = lfilter(self.lowPassB, self.lowPassA, self.unfDataOut)
        else:
            self.dataOut = self.unfDataOut

    @abstractmethod
    def processComp(self, input2): pass


class LowPassFilter(AnalogDevice):
    def processComp(self, input2=0):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        self.compResult = self.dataIn[currentInd]


class Microscopy(AnalogDevice):
    def processComp(self, input2):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        self.compResult = self.gain * input2 * \
                          np.square(self.dataIn[currentInd])


class EOM(AnalogDevice):
    def __init__(self, delayTime, bandWidth, gain, minOut, maxOut):
        AnalogDevice.__init__(self, delayTime, bandWidth, gain)
        self.minOut = minOut
        self.maxOut = maxOut

    def processComp(self, input2):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        tempOut = self.gain * input2 * \
                          self.dataIn[currentInd]
        if (tempOut >= self.minOut) & (tempOut <= self.maxOut):
            self.compResult = tempOut
        elif tempOut <= self.minOut:
            self.compResult = self.minOut
        else:
            self.compResult = self.maxOut


class PMT(AnalogDevice):
    def __init__(self, delayTime, bandWidth, gain, saturation):
        AnalogDevice.__init__(self, delayTime, bandWidth, gain)
        self.saturation = saturation

    def processComp(self, input2=0):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        tempOut = self.gain * \
                  self.dataIn[currentInd]
        if tempOut <= self.saturation:
            self.compResult = tempOut
        else:
            self.compResult = self.saturation


class DAC(AnalogDevice):
    def __init__(self, delayTime):
        AnalogDevice.__init__(self, delayTime, 125, np.divide(1.0, 8191))

    def processComp(self, input2=0):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        if (self.dataIn[currentInd]<=8191) & (self.dataIn[currentInd]>=0):
            self.compResult = self.gain * float(self.dataIn[currentInd])
        elif self.dataIn[currentInd] > 8191:
            self.compResult = 1
        else:
            self.compResult = 0

class ADC(AnalogDevice):
    def __init__(self, delayTime):
        AnalogDevice.__init__(self, delayTime, 125, 8191)

    def processComp(self, input2=0):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        if (self.dataIn[currentInd]<=1) & (self.dataIn[currentInd]>=0):
            self.compResult = self.gain * self.dataIn[currentInd]
        elif self.dataIn[currentInd] > 1:
            self.compResult = 8191
        else:
            self.compResult = 0


class PhotoDidode(AnalogDevice):
    def __init__(self, delayTime, bandWidth, gain, saturation):
        AnalogDevice.__init__(self, delayTime, bandWidth, gain)
        self.saturation = saturation

    def processComp(self, input2=0):
        currentInd = vectorLength - self.delayTime * sampleFreq - 1
        tempOut = self.gain * \
                  self.dataIn[currentInd]
        if tempOut <= self.saturation:
            self.compResult = tempOut
        else:
            self.compResult = self.saturation
