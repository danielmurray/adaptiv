import math
import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def show_graphs(unfiltered, timestamps, cutoff, fs, order=5):
	b, a = butter_lowpass(cutoff, fs, order)

	#Frequency response graph
	w, h = freqz(b, a, worN=8000)
	plt.subplot(2, 1, 1)
	plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
	plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
	plt.axvline(cutoff, color='k')
	plt.xlim(0, 0.5*fs)
	plt.title("Lowpass Filter Frequency Response")
	plt.xlabel('Frequency [Hz]')
	plt.grid()

	filtered = butter_lowpass_filter(unfiltered, cutoff, fs, order)

	plt.subplot(2, 1, 2)
	plt.plot(timestamps, unfiltered, 'r-', label='unfiltered')
	plt.plot(timestamps, filtered, 'g-', linewidth=2, label='filtered')
	plt.xlabel('Time [sec]')
	plt.grid()
	plt.legend()

	plt.subplots_adjust(hspace=0.35)
	plt.show()