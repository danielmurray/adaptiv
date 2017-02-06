from __future__ import print_function

import os
import math
import numpy as np
import lowPass as lp
import sensorData.peakAccelThreshold as pat
import sensorData.stepJerkThreshold as sjt
import sensorData.adaptiveStepJerkThreshold as asjt
import sensorData.adaptiveJerkPaceBuffer as ajpb


def fetch_files(file_path):
    return [file_path + f for f in os.listdir(file_path) if not f.startswith('.')]


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


def android_steps(dir_name):
    f = open(dir_name + '/step.csv')
    step_count = []
    for line in f:
        value = line.split(',')
        if len(value) > 1:
            step = int(float(value[1]))
            step_count.append(step)
    return step_count[-1] - step_count[0] + 1


if __name__ == '__main__':

    # Filter requirements.
    order = 3
    fs = 50.0  # sample rate, Hz
    cutoff = 3.667  # desired cutoff frequency of the filter, Hz

    tests = {
        'mixed': {
            "inHand": 300
        },
        'jog': {
            "inHand": 100,
            "inPocket": 100
        },
        'walk': {
            "inHand": 100,
            "inPocket": 100
        }
    }

    for test, sub_tests in iter(tests.items()):
        print("----------------" + test + "----------------")
        pat_sum = 0
        pjt_sum = 0
        apjt_sum = 0
        ajpb_sum = 0
        andr_sum = 0
        trial_count = 0

        for sub_test in sub_tests:
            # print("----------------"+test+ " " + sub_test + "----------------")
            trials = fetch_files("data/" + test + "/" + sub_test + "/")

            for trial in trials:
                # print("----------------"+trial +"----------------")
                x_data, y_data, z_data, r_data, timestamps = pull_data(trial, 'accelerometer')

                # Filter the data, and plot both the original and filtered signals.
                r = lp.butter_lowpass_filter(r_data, cutoff, fs, order)

                # Peak Acceleration threshold
                crossings = pat.peak_accel_threshold(r, timestamps, 10.5)
                # print("Peak Acceleration Threshold Steps:", len(crossings)/2)
                pat_sum += len(crossings) / 2

                # Peak Jerk Threshold
                jumps, zeroes = sjt.step_jerk_threshold(r, timestamps)
                # print("Step Jerk Threshold Steps:", len(jumps))
                pjt_sum += len(jumps)

                # Adaptive Step Jerk Threshold
                jumps, avgs = asjt.adaptive_step_jerk_threshold(r, timestamps)
                # print("Adaptive Step Jerk Threshold Steps:", len(jumps))
                # print("Final Step Jerk Average:", avgs[-1][1])
                apjt_sum += len(jumps)

                peaks, troughs, avgs = ajpb.adaptive_jerk_pace_buffer(r, timestamps)
                # print("Adaptive Step Jerk Pace Buffer Steps:", len(troughs))
                ajpb_sum += len(peaks)

                # Android Steps
                a_steps = android_steps(trial)
                # print("Android Steps:", a_steps)
                andr_sum += a_steps

                trial_count += 1

        print("Peak Acceleration Average:", pat_sum / trial_count, pat_sum, trial_count)
        print("Step Jerk Average:", pjt_sum / trial_count, pjt_sum, trial_count)
        print("Adaptive Step Jerk Average:", apjt_sum / trial_count, apjt_sum, trial_count)
        print("Adaptive Jerk Pace Buffer Average:", ajpb_sum / trial_count, ajpb_sum, trial_count)
        print("Android Steps:", andr_sum / trial_count, andr_sum, trial_count)
