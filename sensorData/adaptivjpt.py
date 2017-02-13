# Built to complement adaptiv.py

from __future__ import print_function

import numpy as np

# Average seconds per step
# 0.4 seconds
PACE = 400000000
GRAVITY = 10


def learning_count_jerks_pace(data, timestamps):
    last_state = None
    current_state = None
    last_peak = None
    last_trough = None

    peaks = []
    troughs = []
    zero = GRAVITY

    jerk_mean = 1
    pace_mean = PACE
    alpha = 0.125

    jerk_dev = 0.5
    pace_dev = pace_mean / 4
    beta = 0.125

    # Graphing Purpose Array
    # 0 - timestamp
    # 1 - Jerk Mean
    # 2 - Jerk Standard Deviation
    # 3 - Pace Mean
    # 4 - Pace Standard Deviation
    steps = []

    for i, (datum, ts) in enumerate(zip(data, timestamps)):
        milli_ts = ts["milli_ts"]
        nano_ts = ts["nano_ts"]

        if datum < zero and last_state is not None:
            current_state = 'trough'
        elif datum > zero:
            current_state = 'peak'

        if current_state is not last_state:
            # Zero Crossing
            # When coming out of trough assess the "Dip"
            if last_state is 'trough':
                if last_peak and last_trough:

                    jerk = last_peak['val'] - last_trough['val']

                    if jerk > jerk_mean - 2 * jerk_dev:

                        pace = pace_mean
                        if len(peaks) > 1:
                            pace = peaks[-1]['nano_ts'] - peaks[-2]['nano_ts']

                        if pace_mean - 4 * pace_dev < pace < pace_mean + 5 * pace_dev:

                            jerk_dev = abs(jerk_mean - jerk) * beta + jerk_dev * (1 - beta)
                            jerk_mean = jerk * alpha + jerk_mean * (1 - alpha)

                            pace_dev = abs(pace_mean - pace) * beta + pace_dev * (1 - beta)
                            pace_mean = pace * alpha + pace_mean * (1 - alpha)

                            steps.append([
                                last_trough['milli_ts'],
                                last_trough['nano_ts'],
                                jerk,
                                pace,
                                jerk_mean,
                                pace_mean,
                                zero
                            ])
                            troughs.append(last_trough)

                        else:
                            # print("PACE FAIL", pace_mean, pace)
                            if pace > PACE / 2 and abs(pace_mean - pace) < pace_mean * 0.65:
                                pace_dev = abs(pace_mean - pace) * beta + pace_dev * (1 - beta)
                                pace_mean = pace * alpha + pace_mean * (1 - alpha)
                    else:
                        # print("STEP FAIL", jerk_mean, jerk)
                        if jerk > 3 and jerk > jerk_mean * 0.5:
                            jerk_dev = abs(jerk_mean - jerk) * beta + jerk_dev * (1 - beta)
                            jerk_mean = jerk * alpha + jerk_mean * (1 - alpha)

                    new_zero = last_trough['val'] + jerk / 2
                    zero = new_zero * alpha + zero * (1 - alpha)
                last_trough = None
                last_peak = None
            elif last_state is 'peak':
                peaks.append(last_peak)

        if current_state is 'trough' and (last_trough is None or datum < last_trough["val"]):
            last_trough = {
                "milli_ts": milli_ts,
                "nano_ts": nano_ts,
                "val": datum,
                "index": i,
                "min_max": "min"
            }
        elif current_state is 'peak' and (last_peak is None or datum > last_peak["val"]):
            last_peak = {
                "milli_ts": milli_ts,
                "nano_ts": nano_ts,
                "val": float(datum),
                "index": i,
                "min_max": "max"
            }

        last_state = current_state

    return np.array(peaks), np.array(troughs), np.array(steps)
