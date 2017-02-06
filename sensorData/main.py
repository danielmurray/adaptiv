from __future__ import print_function

import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import androidSteps
import lowPass as lp
import peakAccelThreshold as pat
import peakJerkThreshold as pjt
import stepJerkThreshold as sjt
import adaptiveStepJerkThreshold as asjt
import adaptiveJerkPaceThreshold as ajpt
import adaptiveJerkPaceBuffer as ajpb


def pull_data(dir_name, file_name):
    f = open(dir_name + '/' + file_name + '.csv')
    xs = []
    ys = []
    zs = []
    rs = []
    timestamps = []
    for line in f:
        value = line.split(',')
        if len(value) > 3:
            timestamps.append(float(value[0]))
            x = float(value[1])
            y = float(value[2])
            z = float(value[3])
            r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
            xs.append(x)
            ys.append(y)
            zs.append(z)
            rs.append(r)
    return np.array(xs), np.array(ys), np.array(zs), np.array(rs), np.array(timestamps)


def pull_data(dir_name, file_name):
    f = open(dir_name + '/' + file_name + '.csv')
    timestamps = []
    rs = []
    for line in f:
        value = line.split(',')
        if len(value) > 3:
            x = float(value[2])
            y = float(value[3])
            z = float(value[4])
            r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
            timestamp = {
                "milli_ts": value[0],
                "nano_ts": value[1],
            }
            timestamps.append(timestamp)

            rs.append(r)
    return np.array(xs), np.array(ys), np.array(zs), np.array(rs), np.array(timestamps)


if __name__ == '__main__':

    if len(sys.argv) >= 3:
        algo = sys.argv[1]
        trial = sys.argv[2]
    elif len(sys.argv) == 2:
        algo = sys.argv[1]
        trial = 'dan'
    else:
        algo = 'asjt'
        trial = 'dan'

    # Filter requirements.
    order = 3
    fs = 50.0  # sample rate, Hz
    cutoff = 3.667  # desired cutoff frequency of the filter, Hz

    x_data, y_data, z_data, r_data, timestamps = pull_data(trial, 'accelerometer')

    # Filter the data, and plot both the original and filtered signals.
    r = lp.butter_lowpass_filter(r_data, cutoff, fs, order)

    if algo == 'lp':
        # Frequency response graph
        lp.show_graphs(r_data, timestamps, cutoff, fs, order)

    elif algo == 'pat':
        # Peak Acceleration threshold
        crossings = pat.peak_accel_threshold(r, timestamps, 10.5)
        print("Peak Acceleration Threshold Steps:", len(crossings) / 2)

        plt.plot(timestamps, r, 'b-', linewidth=2)
        plt.plot(crossings.T[0], crossings.T[1], 'ro', linewidth=2)
        plt.title(trial + " - Peak Acceleration Threshold")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()

    elif algo == 'pjt':
        # Peak Jerk Threshold
        jerk = pjt.peak_jerk_threshold(r, timestamps)
        plt.plot(jerk.T[0], jerk.T[1], 'g-', linewidth=2)
        plt.title(trial + " - Peak Jerk Threshold")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()

    elif algo == 'sjt':
        # Step Jerk Threshold
        jumps, zeroes = sjt.step_jerk_threshold(r, timestamps)
        ts = [jump['ts'] for jump in jumps]
        val = [jump['val'] for jump in jumps]
        print("Step Jerk Threshold Steps:", len(jumps))

        plt.plot(timestamps, r, 'b-', linewidth=2)
        # plt.plot(zeroes.T[0], zeroes.T[1], 'yo')
        plt.plot(ts, val, 'ro')
        plt.title(trial + " - Step Jerk Threshold")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()

    elif algo == "asjt":
        # Adaptive Step Jerk Threshold
        # Sliding average RTT implementation
        jumps, avgs = asjt.adaptive_step_jerk_threshold(r, timestamps)
        ts = [jump['ts'] for jump in jumps]
        val = [jump['val'] for jump in jumps]
        print("Adaptive Step Jerk Threshold 2 Steps:", len(jumps))
        print("Final Step Jerk Average:", avgs[-1][1])

        plt.plot(timestamps, r, 'b-', linewidth=2)
        plt.plot(ts, val, 'ro')
        plt.plot(avgs.T[0], avgs.T[1], 'r--', linewidth=2)
        plt.plot(avgs.T[0], avgs.T[2], 'g--', linewidth=2)
        plt.title(trial + " - Adaptive Step Jerk Threshold 2")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()

    elif algo == "ajpt":
        # Adaptive Step Jerk Threshold
        peaks, troughs, middles, avgs = ajpt.learning_count_jerks_pace(r, timestamps)
        peak_ts = [peak['ts'] for peak in peaks]
        peak_val = [peak['val'] for peak in peaks]
        trough_ts = [trough['ts'] for trough in troughs]
        trough_val = [trough['val'] for trough in troughs]
        print("Adaptive Jerk Pace Threshold Steps:", len(troughs))
        # print("Final Step Jerk Average:", avgs[-1][1])

        plt.plot(timestamps, r, 'b-', linewidth=2)
        plt.plot(peak_ts, peak_val, 'go')
        plt.plot(trough_ts, trough_val, 'ro')
        # plt.plot(middles.T[0], middles.T[1], 'yo', linewidth=2)
        plt.plot(avgs.T[0], avgs.T[1], 'r--', linewidth=2)
        plt.plot(avgs.T[0], avgs.T[2], 'y--', linewidth=2)
        plt.plot(avgs.T[0], avgs.T[3], 'g--', linewidth=2)
        plt.plot(avgs.T[0], avgs.T[4], 'b--', linewidth=2)
        plt.title(trial + " - Adaptive Step Jerk Threshold")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()

    elif algo == "ajpb":
        # Adaptive Step Jerk Buffer
        peaks, troughs, avgs = ajpb.adaptive_jerk_pace_buffer(r, timestamps)
        peak_ts = [peak['ts'] for peak in peaks]
        peak_val = [peak['val'] for peak in peaks]
        trough_ts = [trough['ts'] for trough in troughs]
        trough_val = [trough['val'] for trough in troughs]
        print("Adaptive Jerk Pace Buffer Steps:", len(troughs))
        # print("Final Step Jerk Average:", avgs[-1][1])

        plt.plot(timestamps, r, 'b-', linewidth=2)
        plt.plot(peak_ts, peak_val, 'go')
        plt.plot(trough_ts, trough_val, 'ro')
        plt.plot(avgs.T[0], avgs.T[1], 'r--', linewidth=2)
        plt.plot(avgs.T[0], avgs.T[2], 'g--', linewidth=2)
        plt.title(trial + " - Adaptive Jerk Pace Buffer")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()

    else:
        # Android
        steps = androidSteps.android_steps(trial)
        pace = np.diff(steps.T[0])
        for i, pace in enumerate(pace):
            print(steps[i][0], pace, steps[i + 1][0])

        print(np.average(pace))

        print("Android Steps:", len(steps))

        plt.plot(timestamps, r, 'b-', linewidth=2)
        plt.plot(steps.T[0], [9.8 for step in steps], 'ro')
        plt.title(trial + " - Android Steps")
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()
        plt.show()
