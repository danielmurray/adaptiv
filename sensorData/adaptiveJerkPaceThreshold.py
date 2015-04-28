import sys
import math
import numpy as np
#Average seconds per step
#0.4 seconds
PACE = 400000000

def learning_count_jerks_pace(data, timestamps):
	
	last_peak = None
	last_trough = None

	peaks = []
	troughs = []
	middles = []
	pace = PACE

	pace_sum = pace
	pace_count = 1
	jerk_sum = 1.5
	jerk_count = 1

	#Graphing Purpose Array
	# 0 - timestamp
	# 1 - Jerk Average
	# 2 - Pace Duration
	avgs = []

	last_pace = timestamps[0]
	for i, datum in enumerate(data):

		timestamp = timestamps[i]
		if timestamp > last_pace + pace:
			# print last_peak, last_trough
			if last_peak is None or last_trough is None:
				break
			jerk =  last_peak['val'] - last_trough['val']
			jerk_avg = jerk_sum/jerk_count

			last_pace = timestamp

			if jerk > jerk_avg * .75:
				# nomalization function
				normalized_jerk = 1.6 - (1.6/(jerk+1))

				jerk_sum = jerk_sum + jerk_avg * normalized_jerk
				jerk_count = jerk_count + 1

				peaks.append(last_peak)
				troughs.append(last_trough)
				print float(pace)/10**8
				jerk_avg = jerk_sum/jerk_count
				avgs.append([
					timestamps[i],
					jerk_avg,
					float(pace)/10**8,
				])


				if len(peaks) > 1:
					pace_sum = pace_sum + peaks[-1]['ts']-peaks[-2]['ts']
					pace_count = pace_count + 1
					pace = pace_sum/pace_count

				first_event = min(last_peak['index'], last_trough['index'])
				second_event = max(last_peak['index'], last_trough['index'])
				last_index = int((second_event - first_event)/2) + first_event
				middles.append([timestamps[last_index], data[last_index]])

			last_trough = None
			last_peak = None

		else:
			if last_trough is None or datum < last_trough["val"]:
				last_trough = {
					"ts": int(float(timestamp)),
					"val": float(datum),
					"index": i,
					"min_max":"min"
				}
			elif last_peak is None or datum > last_peak["val"]:
				last_peak = {
					"ts": int(float(timestamp)),
					"val": float(datum),
					"index": i,
					"min_max":"max"
				}


	return np.array(peaks), np.array(troughs), np.array(middles), np.array(avgs)

