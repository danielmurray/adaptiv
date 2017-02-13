from __future__ import print_function

import numpy as np

PACE = 10


def android_steps(dir_name):
    f = open(dir_name + '/step.csv')
    file_steps = []
    for line in f:
        value = line.split(',')
        if len(value) > 1:
            timestamp = int(float(value[0]))
            step = int(float(value[1]))

            file_steps.append([timestamp, step])

    steps = []
    last_step = file_steps[0]
    for file_step in file_steps:
        steps_taken = file_step[1] - last_step[1]
        time_taken = file_step[0] - last_step[0]
        if steps_taken is 0:
            last_step = file_step
            step = [file_step[0], len(steps) + 1]
            steps.append(step)
        else:
            print("--------" + str(file_step) + "-----------")
            for step_taken in range(1, steps_taken + 1):
                timestamp = last_step[0] + time_taken / steps_taken * step_taken
                step = [timestamp, len(steps) + 1]
                print(step)
                steps.append(step)
            last_step = file_step

    return np.array(steps)
