import sys
import math
import numpy as np
#Average seconds per step
#0.4 seconds
PACE = 400000000
GRAVITY = 10

def learning_count_jerks_pace(data, timestamps):
	
	last_state = None
	current_state = None
	last_peak = None
	last_trough = None

	peaks = []
	troughs = []
	middles = []
	zero = GRAVITY

	jerk_mean = 1
	pace_mean = PACE
	alpha = 0.125
	
	jerk_dev = 0.5
	pace_dev = pace_mean / 4
	beta = 0.125

	#Graphing Purpose Array
	# 0 - timestamp
	# 1 - Jerk Mean
	# 2 - Jerk Standard Deviation
	# 3 - Pace Mean
	# 4 - Pace Standard Deviation
	meta = []

	for i, (datum, timestamp) in enumerate(zip(data,timestamps)):
		
		if datum < zero and last_state is not None:
			current_state = 'trough'
		elif datum > zero:
			current_state = 'peak'

		if current_state is not last_state:
			# Zero Crossing 
			# When coming out of trough assess the "Dip"
			if last_state is 'trough':
				if last_peak and last_trough:

					jerk =  last_peak['val'] - last_trough['val']

					if jerk > jerk_mean - 4*jerk_dev:

						pace = pace_mean
						if len(peaks) > 1 :
							pace = peaks[-1]['ts']-peaks[-2]['ts']

						if pace > pace_mean - 3 * pace_dev and  pace < pace_mean + 5 * pace_dev:

							troughs.append(last_trough)

							jerk_dev = abs(jerk_mean - jerk) * beta + jerk_dev * (1 - beta)
							jerk_mean = jerk * alpha + jerk_mean * (1- alpha)
							
							pace_dev = abs(pace_mean - pace) * beta + pace_dev * (1- beta)
							pace_mean = pace * alpha + pace_mean * (1- alpha)

							meta.append([
								timestamps[i],
								jerk_mean,
								jerk_dev, 
								pace_mean/100000000,
								pace_dev/10000000
							])

							first_event = min(last_peak['index'], last_trough['index'])
							second_event = max(last_peak['index'], last_trough['index'])
							last_index = int((second_event - first_event)/2) + first_event
							middles.append([timestamps[last_index], data[last_index]])
						else:
							print "PACE FAIL", pace_mean, pace
					else:
						print "STEP FAIL"
				last_trough = None
				last_peak = None
			elif last_state is 'peak':
				peaks.append(last_peak)


		if current_state is 'trough' and (last_trough is None or datum < last_trough["val"]):
			last_trough = {
				"ts": timestamp,
				"val": datum,
				"index": i,
				"min_max":"min"
			}
		elif current_state is 'peak' and (last_peak is None or datum > last_peak["val"]):
			last_peak = {
				"ts": timestamp,
				"val": float(datum),
				"index": i,
				"min_max":"max"
			}

		last_state = current_state

	return np.array(peaks), np.array(troughs), np.array(middles), np.array(meta)

