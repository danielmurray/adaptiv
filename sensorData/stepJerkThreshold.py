import numpy as np

GRAVITY = 10


def step_jerk_threshold(data, timestamps):
    last_state = None
    current_state = None
    last_peak = None
    last_trough = None

    peak_troughs = []
    zeroes = []

    zero = GRAVITY

    jerk_threshold = 1.5

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
            zeroes.append([timestamps[i], zero])
            if last_state is 'trough':
                if last_peak:
                    diff = last_peak['val'] - last_trough['val']

                    if diff > jerk_threshold:
                        # nomalization function
                        peak_troughs.append(last_trough)
                last_trough = None
            elif last_state is 'peak':
                # peak_troughs.append(last_peak)
                last_peak = None

        last_state = current_state

    return np.array(peak_troughs), np.array(zeroes)
