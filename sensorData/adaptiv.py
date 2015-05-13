import sys
import math
import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import androidSteps
import lowPass as lp
import adaptivjpt as ajpt
from geopy.distance import vincenty, great_circle
from sklearn.neighbors import KNeighborsClassifier

def pull_data(dir_name, file_name):
	f = open(dir_name + '/' + file_name + '.csv')
	timestamps = []
	rs = []
	for line in f:
		value = line.split(',')
		if len(value) > 4:
			timestamp = {
				"milli_ts":float(value[0]),
				"nano_ts":float(value[1]),
			}
			timestamps.append(timestamp)
			x = float(value[2])
			y = float(value[3])
			z = float(value[4])
			r = math.sqrt(x**2 + y**2 + z**2)
			rs.append(r)
	return np.array(rs), np.array(timestamps)

def write_out(dir_name, data):
	f = open(dir_name + '/adaptiv.csv',"w+")
	for datum in data:
		# print ",".join(datum)
		a =  [str(int(i)) for i in datum]
		f.write(",".join(a)+"\n")


def pull_gps_data(dir_name):
	f = open(dir_name + '/gps.csv')
	data = []
	for line in f:
		value = line.split(',')
		if len(value) > 2:
			lati = float(value[1])
			longi = float(value[2])
			datum = {
				"milli_ts": float(value[0]),
				"latlongs": (lati,longi)
			}
			data.append(datum)
	return np.array(data)

def graph_accel(title, timestamps, r, peaks, troughs, steps):
	nano_ts = [ts['nano_ts'] for ts in timestamps]
	milli_ts = [ts['milli_ts'] for ts in timestamps]
	peak_ts =  [peak['nano_ts'] for peak in peaks]
	peak_val =  [peak['val'] for peak in peaks]
	trough_ts =  [trough['nano_ts'] for trough in troughs]
	trough_val =  [trough['val'] for trough in troughs]
	print "Adaptive Jerk Pace Threshold Steps:", len(steps)
	# print "Final Step Jerk Average:", avgs[-1][1]

	plt.plot(nano_ts, r, 'b-', linewidth=2)
	plt.plot(peak_ts, peak_val, 'go')
	plt.plot(trough_ts, trough_val, 'ro')
	plt.plot(steps.T[1], steps.T[4], 'r--', linewidth=2)
	plt.plot(steps.T[1], steps.T[5]/100000000, 'g--', linewidth=2)
	plt.plot(steps.T[1], steps.T[6], 'y--', linewidth=2)
	plt.title(title + " - Adaptive Step Jerk Threshold")
	plt.xlabel('Time [sec]')
	plt.grid()
	plt.legend()
	plt.show()

def build_training_data(steps_data, gps_data, window_size):

	raw_splits = [ {
		"index": i,
		"start": gps_data[i], 
		"end": gps_data[i+1],
		"steps": []
	}  for i in range(0, len(gps_data)-1) ]

	split_index = 0
	step_index = 0

	while( split_index < len(raw_splits) and step_index < len(steps_data)):
		step = steps_data[step_index]
		step_ts = step[0]
		split = raw_splits[split_index]
		start = split["start"]["milli_ts"]
		end = split["end"]["milli_ts"]		
		if step_ts < start:
			step_index += 1
		elif step_ts > end:
			split_index += 1
		else:
			split["steps"].append(step)
			step_index += 1

	refined_splits =[]
	for raw_split in raw_splits:
		start = raw_split["start"]
		end = raw_split["end"]
		hours = (end["milli_ts"] - start["milli_ts"]) / 1000 / 60 / 60
		distance = great_circle(start["latlongs"], end["latlongs"])
		mph = distance.miles / hours
		if mph < 15 and len(raw_split["steps"]) > 0:
			raw_split["distance"] = distance
			refined_splits.append(raw_split)			

	step_models = []
	for i in range(0,len(refined_splits)-window_size):
		splits = refined_splits[i:i+window_size+1]
		distance = np.sum([split["distance"] for split in splits])
		steps = []
		for split in splits:
			for step in split["steps"]:
				steps.append(step)
		avg_jerk = np.sum([step[2] for step in steps]) / len(steps)
		avg_pace = np.sum([step[3] for step in steps]) / len(steps)
		avg_stride = distance / len(steps)
		step_models.append([avg_jerk, avg_pace, avg_stride])
	return step_models


def train(window_size):

	dirs = [
		"walk_halfmile",
		"litejog_halfmile",
		"jog_mile",
		"sprint_halfmile"
	]

	order = 3
	fs = 50.0       # sample rate, Hz
	cutoff = 5 # desired cutoff frequency of the filter, Hz

	cum_step_train_data = []

	for directory in dirs:
		r_data, timestamps = pull_data("gpsdata/train/"+directory, "accelerometer")
		r = lp.butter_lowpass_filter(r_data, cutoff, fs, order)
		peaks, troughs, steps = ajpt.learning_count_jerks_pace(r, timestamps)
		write_out("gpsdata/train/"+directory, steps)
		
		gps_data = pull_gps_data("gpsdata/train/"+directory)
		step_train_data = build_training_data(steps, gps_data, window_size)
		print len(step_train_data)
		for i in step_train_data:
			cum_step_train_data.append(i)

	return cum_step_train_data

def graph_distance(title, gps_data, actual_distances, steps, est_dists):
	act_dests = []
	act_dest_cum = []
	act_dest_sum = vincenty((0,0),(0,0))

	est_dests = []
	est_dest_cum = []
	est_dest_sum = vincenty((0,0),(0,0))

	for i in range(0,len(gps_data)-1):
		ts = gps_data[i]['milli_ts']
		act_dest = actual_distances[i]
		act_dests.append([ts, act_dest.meters])
		act_dest_sum += act_dest
		act_dest_cum.append([ts, act_dest_sum.miles])

	print len(steps), len(est_dists)
	for step, est_dest in zip(steps, est_dists):
		ts = step[0]
		est_dests.append([ts, est_dest.meters])
		est_dest_sum += est_dest
		est_dest_cum.append([ts, est_dest_sum.miles])


	#Actual
	act_dest_cum = np.array(act_dest_cum)
	plt.plot(act_dest_cum.T[0], act_dest_cum.T[1], 'b-', linewidth=2)

	#Estimated
	est_dest_cum = np.array(est_dest_cum)
	plt.plot(est_dest_cum.T[0], est_dest_cum.T[1], 'r-', linewidth=2)

	print act_dest_cum[-1], est_dest_cum[-1], np.sum(est_dists).miles

	plt.title(title+" Actual vs Estimated Distance")
	plt.xlabel('Time [sec]')
	plt.ylabel('Cumulative Distance [miles]')
	plt.grid()
	plt.legend()
	plt.show()
	# plt.savefig("../imgs/act_vs_est_sum/"+title+".png")
	plt.clf()


def test(train_data_labels, k):


	dirs = [
		"mile",
		"800step",
		"joghome",
		"walk_halfmile",
		"litejog_halfmile",
		"jog_mile",
		"sprint_halfmile"
	]

	order = 3
	fs = 60.0       # sample rate, Hz
	cutoff = 5  # desired cutoff frequency of the filter, Hz
	
	train_data = [ d[0:2] for d in train_data_labels]
	train_labels = [ d[2] for d in train_data_labels]

	neigh = KNeighborsClassifier(n_neighbors=k, algorithm="auto")
	neigh.fit(train_data, train_labels)

	for directory in dirs:
		r_data, timestamps = pull_data("gpsdata/test/"+directory, "accelerometer")
		r = lp.butter_lowpass_filter(r_data, cutoff, fs, order)
		peaks, troughs, steps = ajpt.learning_count_jerks_pace(r, timestamps)
		# graph_accel(directory, timestamps, r, peaks, troughs, steps)

		gps_data = pull_gps_data("gpsdata/test/"+directory)
		actual_distances = [ great_circle(gps_data[i]["latlongs"],gps_data[i+1]["latlongs"]) for i in range(0,len(gps_data)-1)]
		actual_distance = np.sum(actual_distances)

		train_data = [ d[2:4] for d in steps]
		test_labels = neigh.predict(train_data)
		est_dist = np.sum(test_labels)

		print (est_dist-actual_distance) / actual_distance * 100, "%"
		# graph_distance(directory, gps_data, actual_distances, steps, test_labels)



if __name__ == '__main__':
	train_data = train(4)
	test(train_data, 1)













