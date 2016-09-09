import analog_device
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
# generate a sine wave with certain frequency
sampleFreq = 10
f = 0.05
sampleNum = 1000
xSin = np.arange(sampleNum)
ySin = np.sin(2 * np.pi * f * xSin / sampleFreq) + npr.rand(1000)/5
plt.figure(1)
plt.subplot(211)
plt.plot(xSin, ySin)
plt.title("Input Signal")

outArray = np.zeros(1000)
TestClass = analog_device.LowPassFilter(10, 1)
TestClass.deviceIni(np.zeros(50), np.zeros(50))
for i in range(0, 1000, 1):
    TestClass.dataIn[0:-2] = TestClass.dataIn[1:-1]
    TestClass.dataIn[-1] = ySin[i]
    TestClass.processComp(0)
    TestClass.outputComp()
    outArray[i] = TestClass.dataOut[-1]
plt.subplot(212)
plt.plot(xSin, outArray)
plt.title("Output Signal")
plt.show()
