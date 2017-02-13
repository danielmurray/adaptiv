from __future__ import print_function

import collections
import numpy as np

# Average seconds per step
# 0.4 seconds
PACE = 400000000
PACE_BUFFER_MAX = 20

# Average step jerk
# 2.5 m/s**3
JERK = 2.5
JERK_BUFFER_MAX = 20


class StepDecider:
    def __init__(self, pace_buffer_max, jerk_buffer_max):
        self.jerk_buffer = collections.deque(maxlen=jerk_buffer_max)
        self.jerk_buffer.append(JERK)

        self.pace_buffer = collections.deque(maxlen=pace_buffer_max)
        self.pace_buffer.append(PACE)

        self.last_peak = None
        self.last_trough = None

        # Graphing Purpose Array
        # 0 - timestamp
        # 1 - Jerk Average
        # 2 - Pace Duration
        self.avgs = []

    def decide(self, peak, trough):
        # Given a peak and a trough, determine if the jerk spike
        # and pace spacing is a step

        jerk_avg = sum(self.jerk_buffer) / len(self.jerk_buffer)
        pace_avg = sum(self.pace_buffer) / len(self.pace_buffer)

        jerk = peak['val'] - trough['val']
        pace = abs(peak['ts'] - trough['ts'])

        if self.last_peak and self.last_trough:
            peak_pace = peak['ts'] - self.last_peak['ts']
            trough_pace = trough['ts'] - self.last_trough['ts']
            # print(peak_pace, trough_pace)

            # print('peak', self.last_peak['ts'], peak['ts'], peak_pace)
            # print('trough', self.last_trough['ts'], trough['ts'], trough_pace)

            pace = max(peak_pace, trough_pace)
        else:
            pace = pace_avg

        self.last_peak = peak
        self.last_trough = trough

        self.avgs.append([
            max(peak['ts'], trough['ts']),
            jerk_avg,
            float(pace_avg) / 10 ** 8,
        ])

        # print('jerk', jerk, jerk_avg, jerk > jerk_avg * .5)
        if jerk >= jerk_avg * .5 or jerk >= JERK * 2:
            # print('pace', float(pace)/10**8, float(pace_avg)/10**8, pace >= pace_avg * .5, pace <= pace_avg * 2, pace >= pace_avg * .5 and pace <= pace_avg * 2)
            if pace_avg * .5 <= pace <= pace_avg * 2:
                self.jerk_buffer.append(jerk)
                self.pace_buffer.append(pace)

                return True
            else:
                return False
        else:
            return False

    def get_avgs(self):
        return self.avgs


def adaptive_jerk_pace_buffer(data, timestamps):
    last_peak = None
    last_trough = None
    last_datum = None
    last_slope = None

    peaks = []
    troughs = []

    sd = StepDecider(PACE_BUFFER_MAX, JERK_BUFFER_MAX)

    for i, datum in enumerate(data):

        timestamp = timestamps[i]

        if last_datum:
            if datum > last_datum:
                slope = 'rising'
            elif datum < last_datum:
                slope = 'falling'

            if last_slope and last_slope is not slope:

                if slope is 'falling':
                    # Maximum
                    potential_peak = {
                        "ts": int(float(timestamp)),
                        "val": float(datum),
                        "index": i,
                        "min_max": "max"
                    }

                    if last_trough:
                        # print('trough?')
                        if sd.decide(potential_peak, last_trough):
                            # print('trough added')
                            troughs.append(last_trough)
                            # last_peak = potential_peak
                    # 	elif last_peak is None or  potential_peak['val'] > last_peak['val']:
                    # 		last_peak = potential_peak
                    # else:
                    last_peak = potential_peak

                if slope is 'rising':
                    # Minimum
                    potential_trough = {
                        "ts": int(float(timestamp)),
                        "val": float(datum),
                        "index": i,
                        "min_max": "min"
                    }

                    if last_peak:
                        # print('peak?')
                        if sd.decide(last_peak, potential_trough):
                            # print('peak added')
                            peaks.append(last_peak)
                            # last_trough = potential_trough
                    # 	elif last_trough is None or potential_trough['val'] < last_trough['val']:
                    # 		last_trough = potential_trough
                    # else:
                    last_trough = potential_trough

            last_slope = slope
        last_datum = datum
    # print(i)

    return np.array(peaks), np.array(troughs), np.array(sd.avgs)
