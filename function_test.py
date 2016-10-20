import numpy as np
import matplotlib.pyplot as plt

image = np.load('./input/hdr_neuron.npy')
plt.imshow(image, cmap='Greys_r')
plt.show()
