import analog_device
import numpy as np
TestClass = analog_device.LowPassFilter(0, 0)
TestClass.deviceIni(np.ones(50), np.zeros(50))
TestClass.outputComp()
print TestClass.dataOut
