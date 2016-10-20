from scipy import misc
import matplotlib.pyplot as plt
import numpy as np
neuron_raw = misc.imread('./input/neuron.jpg')
neuron_b = 0.299*neuron_raw[:, :, 0] + 0.587*neuron_raw[:, :, 1] +\
           0.114*neuron_raw[:, :, 2]

second_to_0_bias = 0.5
neuron_b[neuron_b == 0] = second_to_0_bias

neuron_b *= 4
neuron_b -= second_to_0_bias
neuron_c = neuron_b[150:249,150:249]
plt.figure(1)
plt.imshow(neuron_c, cmap='Greys_r')
# plt.figure(2)
# plt.hist(neuron_b, bins='auto')
plt.show()
print np.amax(neuron_b)
print np.amin(neuron_b)
np.save('./input/hdr_neuron', neuron_c)
