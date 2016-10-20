import analog_device
import FPGA
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
import math
from tqdm import tqdm
# pid parameters
sp_set = 3000; kp_set = 270; ki_set = 33; kd_set = 0
pmax_set = 8000; integrator_set = 35000000;

#  load image and some pre-processing
ground_image = np.load('./input/hdr_neuron.npy')
img_rows = ground_image.shape[0]
img_cols = ground_image.shape[1]
line_image = np.reshape(ground_image, [img_cols*img_rows, 1])

# zero pad the line image to mimic when the long wait before start scanning
pixel_time = 4
sampling_freq = 125

zero_pad = np.zeros([2000/(pixel_time*sampling_freq), 1])
line_image = np.append(zero_pad, line_image)
# line_image = line_image[0:80]
interp_x = np.arange(pixel_time * sampling_freq * line_image.shape[0])
interp_image = np.interp(interp_x, np.linspace(0, line_image.shape[0] * pixel_time * sampling_freq, line_image.shape[0]), line_image)

simulation_span = 500
sample_num = line_image.shape[0] * pixel_time * sampling_freq

pid_input_array = np.zeros(sample_num)
pid_output_array = np.zeros(sample_num)
x_output_array = np.zeros(sample_num)
dac_output_array = np.zeros(sample_num)
eom_output_array = np.zeros(sample_num)
microscope_output_array = np.zeros(sample_num)
pmt_output_array = np.zeros(sample_num)
pid_error_array = np.zeros(sample_num)
pid_kp_array = np.zeros(sample_num)
pid_integrator_array = np.zeros(sample_num)
pid_pin_array = np.zeros(sample_num)
laserPower = np.ones(sample_num)
x_current = np.ones(sample_num)
x_origin = np.ones(sample_num)
x_ave = np.zeros(line_image.shape[0])
# device declaration and initiation (delayTime, bandWidth, gain)
eoModulator = analog_device.EOM(0.4, 0.8, 1, 0.01, 10)
eoModulator.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
tpMicroscope = analog_device.Microscopy(0, 125, 0.005)
tpMicroscope.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
pmTube = analog_device.PMT(0.2, 50, 100, 4)
pmTube.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
pDidode = analog_device.PhotoDidode(0.2, 2, 1, 2)
pDidode.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
outputLP = analog_device.LowPassFilter(0.1, 1, 1)
outputLP.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
daConverter = analog_device.DAC(0.04)
daConverter.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
adConverter = analog_device.ADC(0.04)
adConverter.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
adConverter2 = analog_device.ADC(0.04)
adConverter2.deviceIni(np.zeros(simulation_span), np.zeros(simulation_span))
pidController = FPGA.PID(sp_set, kp_set, ki_set, kd_set, pmax_set, integrator_set)
xLog = FPGA.LogComputation()

# imaging loop
for i in tqdm(range(0, sample_num, 1)):
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
    tpMicroscope.processComp(interp_image[i])
    tpMicroscope.outputComp()
    microscope_output_array[i] = tpMicroscope.dataOut[-1]

    pmTube.dataIn = tpMicroscope.dataOut
    pmTube.processComp()
    pmTube.outputComp()
    pmt_output_array[i] = pmTube.dataOut[-1]

    # outputLP.dataIn = pmTube.dataOut
    # outputLP.processComp()
    # outputLP.outputComp()
    #
    # adConverter.dataIn = outputLP.dataOut
    adConverter.dataIn = pmTube.dataOut

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

    pid_pin_array[i] = xLog.pIn
    x_ave[i/(pixel_time*sampling_freq)] += x_output_array[i]
    x_current[i] = interp_image[i]
x_origin = np.delete(line_image, np.arange(2000/(pixel_time*sampling_freq)))
x_ave = np.delete(x_ave, np.arange(2000/(pixel_time*sampling_freq)))
x_ave = x_ave / (pixel_time*sampling_freq) * 8191 / 2048
x_rec = np.power(10, x_ave * 2 * math.log10(8191) / 8191) * 8050
x_reshape = np.reshape(x_rec, [img_rows, img_cols])
x_plot = np.arange(sample_num)
plt.figure(1)
plt.subplot(521)
plt.plot(x_plot, dac_output_array)
plt.title("kp = %d, ki = %d, kd = %d, sp = %d, pmax = %d, limit = %d"%(kp_set, ki_set, kd_set, sp_set, pmax_set, integrator_set))
plt.ylabel("DAC Output Signal")
plt.subplot(523)
plt.plot(x_plot, eom_output_array)
plt.ylabel("EOM Output Signal")
plt.subplot(525)
plt.plot(x_plot, microscope_output_array)
plt.ylabel("Microscope Output Signal")
# plt.subplot(523)
# plt.plot(x_plot, pmt_output_array)
# plt.ylabel("PMT Output Signal")
plt.subplot(527)
plt.plot(x_plot, pid_pin_array)
plt.ylabel("Log P_in Signal")
# plt.subplot(525)
# plt.plot(x_plot, pid_input_array)
# plt.ylabel("log S_in Signal")
plt.subplot(529)
plt.plot(x_plot, x_output_array)
plt.ylabel("X Output Signal")
plt.subplot(522)
plt.plot(x_plot, pid_input_array)
plt.ylabel("PID Input Signal")
plt.subplot(524)
plt.plot(x_plot, x_current)
plt.ylabel("Current X")
plt.subplot(526)
plt.plot(x_plot, pid_kp_array)
plt.ylabel("Kp Signal")
plt.subplot(528)
plt.plot(x_plot, pid_integrator_array)
plt.ylabel("Integrator")
plt.subplot(5, 2, 10)
plt.plot(x_plot, pid_output_array)
plt.ylabel("PID Output")


plt.figure(2)
plt.subplot(3, 1, 1)
plt.plot(x_ave)
plt.ylabel("Ave_log")
plt.subplot(3, 1, 2)
plt.plot(x_rec)
plt.ylabel("Reconstruction")
plt.subplot(3, 1, 3)
plt.plot(x_origin)
plt.ylabel("Ground")

plt.figure(3)
plt.subplot(2,1,1)
plt.imshow(ground_image, cmap='Greys_r')
plt.ylabel("Ground Image")
plt.subplot(2,1,2)
plt.imshow(x_reshape, cmap='Greys_r')
plt.ylabel("Reconstructed Image")
plt.show()

