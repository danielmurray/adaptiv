import numpy as np


def derive(data, timestamps):
    derivatives = []
    for i in range(0, len(data) - 1):
        delta_y = data[i + 1] - data[i]
        delta_t = timestamps[i + 1] - timestamps[i]
        derivative = delta_y / delta_t
        timestamp = timestamps[i] + delta_t / 2
        derivatives.append([timestamp, derivative])
    return np.array(derivatives)
