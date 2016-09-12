import analog_device
import FPGA
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
# generate a sine wave with certain frequency
sampleFreq = 125
f = 1
sampleNum = 6000
xSin = np.arange(sampleNum)
ySin = np.sin(2 * np.pi * f * xSin / sampleFreq) + npr.rand(sampleNum)/5 + 1.5

# laser power
laserPower = np.ones(sampleNum)
# image
x0 = np.zeros(sampleNum/6).astype(float)
x1 = np.ones(sampleNum/6*5).astype(float)
x = np.concatenate((x0, x1))

pid_input_array = np.zeros(sampleNum)
pid_output_array = np.zeros(sampleNum)
x_output_array = np.zeros(sampleNum)
dac_output_array = np.zeros(sampleNum)
eom_output_array = np.zeros(sampleNum)
microscope_output_array = np.zeros(sampleNum)
pmt_output_array = np.zeros(sampleNum)
pid_error_array = np.zeros(sampleNum)
pid_kp_array = np.zeros(sampleNum)
pid_integrator_array = np.zeros(sampleNum)

# device declaration and initiation
eoModulator = analog_device.EOM(0.4, 2, 1, 0.01, 10)
eoModulator.deviceIni(np.zeros(200), np.zeros(200))
tpMicroscope = analog_device.Microscopy(0, 125, 0.005)
tpMicroscope.deviceIni(np.zeros(200), np.zeros(200))
pmTube = analog_device.PMT(0.2, 50, 10000, 4)
pmTube.deviceIni(np.zeros(200), np.zeros(200))
pDidode = analog_device.PhotoDidode(0.2, 20, 4, 2)
pDidode.deviceIni(np.zeros(200), np.zeros(200))
outputLP = analog_device.LowPassFilter(0.04, 1, 1)
outputLP.deviceIni(np.zeros(200), np.zeros(200))
daConverter = analog_device.DAC(0.04)
daConverter.deviceIni(np.zeros(200), np.zeros(200))
adConverter = analog_device.ADC(0.04)
adConverter.deviceIni(np.zeros(200), np.zeros(200))
adConverter2 = analog_device.ADC(0.04)
adConverter2.deviceIni(np.zeros(200), np.zeros(200))
pidController = FPGA.PID(2000, 1, 5, 0, 1500, 10000000)
xLog = FPGA.LogComputation()
# imaging loop
for i in range(0, sampleNum, 1):
    daConverter.dataIn[0:-1] = daConverter.dataIn[1:]
    daConverter.dataIn[-1] = pidController.DACOutput()
    daConverter.processComp()
    daConverter.outputComp()
    dac_output_array[i] = daConverter.dataOut[-1]

    # eoModulator.dataIn[0:-1] = eoModulator.dataIn[1:]
    # eoModulator.dataIn[-1] = ySin[i]
    eoModulator.dataIn = daConverter.dataOut
    eoModulator.processComp(laserPower[i])
    eoModulator.outputComp()
    eom_output_array[i] = eoModulator.dataOut[-1]

    pDidode.dataIn = eoModulator.dataOut
    pDidode.processComp()
    pDidode.outputComp()
    adConverter2.dataIn = pDidode.dataOut
    adConverter2.processComp()
    adConverter2.outputComp()

    tpMicroscope.dataIn = eoModulator.dataOut
    tpMicroscope.processComp(x[i])
    tpMicroscope.outputComp()
    microscope_output_array[i] = tpMicroscope.dataOut[-1]

    pmTube.dataIn = tpMicroscope.dataOut
    pmTube.processComp()
    pmTube.outputComp()
    pmt_output_array[i] = pmTube.dataOut[-1]

    outputLP.dataIn = pmTube.dataOut
    outputLP.processComp()
    outputLP.outputComp()

    adConverter.dataIn = outputLP.dataOut
    adConverter.processComp()
    adConverter.outputComp()
    pid_input_array[i] = adConverter.dataOut[-1]
    pidController.ADCInput(adConverter.dataOut[-1])
    pidController.PIDComp()
    pid_error_array[i] = pidController.error
    pid_kp_array[i] = pidController.kpTer
    pid_integrator_array[i] = pidController.integrator
    pid_output_array[i] = pidController.DACOutput()

    xLog.sIn = int(adConverter.dataOut[-1])
    xLog.pIn = int(adConverter2.dataOut[-1])
    xLog.logAndSubtraction()
    xLog.DAAD()
    x_output_array[i] = xLog.logX

plt.figure(1)
plt.subplot(521)
plt.plot(xSin, dac_output_array)
plt.ylabel("DAC Output Signal")
plt.subplot(523)
plt.plot(xSin, eom_output_array)
plt.ylabel("EOM Output Signal")
plt.subplot(525)
plt.plot(xSin, microscope_output_array)
plt.ylabel("Microscope Output Signal")
plt.subplot(527)
plt.plot(xSin, pmt_output_array)
plt.ylabel("PMT Output Signal")
plt.subplot(529)
plt.plot(xSin, x_output_array)
plt.ylabel("X Output Signal")
plt.subplot(522)
plt.plot(xSin, pid_input_array)
plt.ylabel("PID Input Signal")
plt.subplot(524)
plt.plot(xSin, pid_error_array)
plt.ylabel("Error Signal")
plt.subplot(526)
plt.plot(xSin, pid_kp_array)
plt.ylabel("Kp Signal")
plt.subplot(528)
plt.plot(xSin, pid_integrator_array)
plt.ylabel("Integrator")
plt.subplot(5, 2, 10)
plt.plot(xSin, pid_output_array)
plt.ylabel("PID Output")
plt.show()
