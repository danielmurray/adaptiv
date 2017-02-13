import numpy as np

GRAVITY = 10


def adaptive_step_jerk_threshold_old(data, timestamps):
    last_state = None
    current_state = None
    last_peak = None
    last_trough = None

    peak_troughs = []
    zero = GRAVITY

    jerk_sum = 1
    jerk_count = 1

    # Graphing Purpose Array
    # 0 - timestamp
    # 1 - Jerk Average
    averages = []

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
                    jerk_avg = jerk_sum / jerk_count

                    if jerk > jerk_avg * .75:
                        # nomalization function
                        normalized_jerk = 1.6 - (1.6 / (jerk + 1))

                        jerk_sum += jerk_avg * normalized_jerk
                        jerk_count += 1

                        peak_troughs.append(last_trough)

                        jerk_avg = jerk_sum / jerk_count
                        averages.append([
                            timestamps[i],
                            jerk_avg
                        ])

                last_trough = None
            elif last_state is 'peak':
                # peak_troughs.append(last_peak)
                last_peak = None

        last_state = current_state

    return np.array(peak_troughs), np.array(averages)
