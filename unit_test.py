import analog_device
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
# generate a sine wave with certain frequency
sampleFreq = 10
f = 0.05
sampleNum = 1000
xSin = np.arange(sampleNum)
ySin = np.sin(2 * np.pi * f * xSin / sampleFreq) + npr.rand(1000)/5 + 1.5
plt.figure(1)
plt.subplot(211)
plt.plot(xSin, ySin)
plt.title("Input Signal")
# laser power
laserPower = np.ones(1000)
# image
x0 = np.ones(500).astype(float)
x1 = np.ones(500).astype(float) * 2
x = np.concatenate((x0, x1))

outArray = np.zeros(1000)
# device declaration and initiation
eoModulator = analog_device.EOM(1, 1, 2, 0.01, 10)
eoModulator.deviceIni(np.zeros(50), np.zeros(50))
tpMicroscope = analog_device.Microscopy(0, 999, 0.005)
tpMicroscope.deviceIni(np.zeros(50), np.zeros(50))
pmTube = analog_device.PMT(0.2, 50, 20, 4)
pmTube.deviceIni(np.zeros(50), np.zeros(50))
outputLP = analog_device.LowPassFilter(1, 1, 1)
outputLP.deviceIni(np.zeros(50), np.zeros(50))
# imaging loop
for i in range(0, 1000, 1):
    eoModulator.dataIn[0:-1] = eoModulator.dataIn[1:]
    eoModulator.dataIn[-1] = ySin[i]
    eoModulator.processComp(laserPower[i])
    eoModulator.outputComp()
    tpMicroscope.dataIn = eoModulator.dataOut
    tpMicroscope.processComp(x[i])
    tpMicroscope.outputComp()
    pmTube.dataIn = tpMicroscope.dataOut
    pmTube.processComp()
    pmTube.outputComp()
    outputLP.dataIn = pmTube.dataOut
    outputLP.processComp()
    outputLP.outputComp()
    outArray[i] = outputLP.dataOut[-1]

plt.subplot(212)
plt.plot(xSin, outArray)
plt.title("Output Signal")
plt.show()
