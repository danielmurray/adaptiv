import numpy as np

GRAVITY = 10


def adaptive_step_jerk_threshold(data, timestamps):
    last_state = None
    current_state = None
    last_peak = None
    last_trough = None

    peak_troughs = []
    zero = GRAVITY

    jerk_mean = 1
    alpha = 0.125

    jerk_dev = 0.5
    beta = 0.25

    # Graphing Purpose Array
    # 0 - timestamp
    # 1 - Jerk Mean
    # 2 - Jerk Standard Deviation
    meta = []

    for i, datum in enumerate(data):

        if datum < zero and last_state is not None:
            current_state = 'trough'
            if last_trough is None or datum < last_trough["val"]:
                last_trough = {
                    "ts": timestamps[i],
                    "val": data[i],
                    "min_max": "min"
                }
        elif datum > zero:
            current_state = 'peak'
            if last_peak is None or datum > last_peak["val"]:
                last_peak = {
                    "ts": timestamps[i],
                    "val": data[i],
                    "min_max": "max"
                }

        if current_state is not last_state:
            # Zero Crossing
            # When coming out of trough assess the "Dip"
            if last_state is 'trough':

                if last_peak:

                    jerk = last_peak['val'] - last_trough['val']

                    if jerk > jerk_mean - 4 * jerk_dev:
                        jerk_dev = abs(jerk_mean - jerk) * beta + jerk_dev * (1 - beta)
                        jerk_mean = jerk * alpha + jerk_mean * (1 - alpha)

                        peak_troughs.append(last_trough)

                        meta.append([
                            timestamps[i],
                            jerk_mean,
                            jerk_dev
                        ])

                last_trough = None
            elif last_state is 'peak':
                # peak_troughs.append(last_peak)
                last_peak = None

        last_state = current_state

    return np.array(peak_troughs), np.array(meta)
