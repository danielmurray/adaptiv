Adaptiv: An Adaptive Jerk Pace Buffer Step Detection Algorithm
===========

- Dan Murray
- Ryan Bolick

##Abstract
Mobile consumer technology today is equipped with a myriad of sophisticated sensors capable of measuring multiple environment variables. One of the most exciting sensors on most mobile devices today is the accelerometer, capable of measuring the device's proper acceleration, i.e. acceleration relative to free fall. Proper acceleration data has many uses in today's mobile applications ranging from, determining the device's orientation, gesture recognition, and detecting user movement, namely step detection. In this git repository we explore the use of android's raw accelerometer data in the application of step detection. Step detection has many uses in today's mobile computing field, including activity tracking as well as providing correction in indoor localization methods. Noticing this significance of accurate step detection, the goal of this repository was to explore a few algorithms in precise step detection.

##Introduction
In this repository we will introduce our algorithm, Adaptiv, an adaptive jerk pace buffer step detection algorithm. First we will explain our method of data collection and filtering, then we will discuss the iterations our step detection algorithm design took that led us to our final implementation.

##Collection (Android App)
In the app file you will find our Android app responsible for logging the accelerometer sensor data and writing that data out to CSV file in external storage. The application itself is a single activity dynamically being updated with the devices live accelerometer data. The bottom row is the Android built-in step detection sensor data, to serve as a reference. At the top is the button that initializes and terminates the trial collection.

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/screenshot.png" />
</p>

##Filtering
The accelerometer data provided by the android service is fairly noisy. High frequency oscillations from the device and ambient environment skew the clean oscillations of a user's natural step. In order to remove this noise, we put the acceleration data through a lowpass band filter to remove the noise and give us a cleaner signal to work with. Below you can see the implemented low pass filter band with a 3.6667 Hz cut-off, as well as the resulting filtered data overlaid on top of the unfiltered raw data.

```bash
bash$ python sensordata/main.py lp
```

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/lowpassfilter.png" />
</p>

##Step Counting Algorithms
Once filtered we may then begin implementing step detection algorithms. In this section we will discuss the process that brought us to the Adaptiv, adaptive jerk threshold, method. As a quick note, the blue line data you see in the following graphs is the filtered *r* data. *R* is the scalar magnitude of the three combined acceleration data points: *x*, *y*, and *z*. The advantage of using *r* versus any particular acceleration data direction is that it is impartial to device orientation and can handle dynamic reorientations of the device. How we calculate *r* is given below.

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/r_equation.png" />
</p>

###Peak Acceleration Threshold
Our first iteration is the standard peak threshold algorithm. We count the number of spikes by setting a threshold and counting the times the data crosses that threshold. The number of steps should be equal to the number of crossings divided by two. On our first iterations we looked at Dan's 100-step trial with a threshold of 10.5

```bash
bash$ python sensordata/main.py pat data/walk/inHand/dan1
```
<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/dan_100_single_peak.png" />
</p>

Each red dot represents a crossing of our threshold, and as you can see, this algorithm is quite effective at pinpointing the peaks and the resulting steps. In fact, in the above test case, after taking 100 steps the program counted 101 steps, that is 1% error.
However, when applying the same algorithm and threshold to Zhang's 100-step trial, the program only counted 88 steps. In the graph below we see how Zhang's walking style results in steps that do not break the threshold.

```bash
bash$ python sensordata/main.py pat data/walk/inHand/zhang
```
<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/zhang_100_single_peak.png" />
</p>

What we concluded was that a static threshold is not a reliable method for counting steps of individuals with different walking styles. If you lowered the threshold to accept more "glide" walkers, you may be getting false positives for the more "stomp" walkers. We figured this was an unsatisfactory approach.

###Peak Jerk Threshold
The issues of uncommon gaits seemed troublesome. However, what was common throughout Zhang and Dan's gaits was the major drop from peak to trough. We figured if we went deeper, i.e. derived the acceleration data, we could perhaps extract this peak change in acceleration, otherwise known as jerk. So we derived each acceleration data point at index *i* to find j, or jerk. Where *t* is the timestamp at index *i*. 


<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/derivative.png" />
</p>

We then graphed the resulting jerk data points...

```bash
bash$ python sensordata/main.py pjt data/walk/inHand/dan1
```

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/dan_100_jerk.png" />
</p>

What we found was that the resulting jerk data set was just as noisy, if not noisier than the orignial acceleration data. We figured that deriving the accelerometer data provided no cleared distinction of a user's step.

###Step Jerk Threshold
We knew these large spikes in jerk were significant, so in our next algorithm we sought out identifying these peaks and troughs programmatically. We achieved this by identifying the crest and trough within a single oscillation. We define an oscillation as three consecutive zero crossings, points A, C, and E in the graph shown below. In our example, a zero crossing is defined by the moment when acceleration is equal to gravity.

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/wave.gif" />
</p>

In the graph below, red dots are the crest and troughs, and yellow dots are the zero crossings.

```bash
bash$ python sensordata/main.py sjt data/walk/inHand/dan1
```
<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/dan_100_jerkstep.png" />
</p>

We then calculate the change from crest to trough, we call this value Step Jerk. If this value is greater than the threshold we consider the oscillation a step. In the following trial we look at Dan's 100 steps with a step threshold of 1.5. 

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/dan_100_jerkstep2.png" />
</p>

In the graph above we mark all valid step troughs with a red dot. Again, as you can see this algorithm is quite effective at pinpointing the steps. The above trial counted 98 steps.
However, yet again, when applying this algorithm to a different walking gait, we receive poor results. Testing Zhang's 100-step trial, the program only counted 48 steps, an even worse result. In the graph below we see how Zhang's walking style results in steps that do not break the jerk threshold.

```bash
bash$ python sensordata/main.py sjt data/walk/inHand/zhang
```

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/zhang_100_jerkstep.png" />
</p>

We were right back to where we started, however we felt we were on to something. We figured if the step jerk could adapt to the user, and the situation, the algorithm would be better suited to count steps. So we developed a method to do just that...

###Adaptive Step Jerk Threshold
The intuition of this method is to allow the algorithm to adapt to the user's gait. We accomplish this by dynamically updating a step jerk average threshold, *SJA*, each time a step is detected. A step being defined as a step jerk, *j*, greater than 65% of the *SJA*. *SJA* being defined as the step jerk sum, *SJS*, divided by the numer of step jerks, *i*.

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/condition.png" />
</p>
<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/sja_equation.png" />
</p>

If a jerk step is considered a step it is normalized, multiplied by the previous average, *SJA*, then added to the step jerk sum, *SJS*.

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/normalized_j.png" />
</p>
<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/sjs_equation.png" />
</p>

We initialize the step jerk average threshold to 1.5, as it seems a logical average for user step, and then we run the algorithm for Dan's 100-step trial. The red dashed line is the SJA as it is dynamically updated.

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/init.png" />
</p>

```bash
bash$ python sensordata/main.py asjt data/walk/inHand/dan1
```

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/dan_100_adaptivestepjerk.png" />
</p>
Again, in the graph above we mark all valid step troughs with a red dot. The algorithm is quite effective at pinpointing the steps with a count of 102 steps, and a final average SJA of about 1.3 m/s^3.

Now for the moment of truth, with this algorithm also be able to adapt to Zhang's more gentle walking pattern...

```bash
bash$ python sensordata/main.py asjt data/walk/inHand/zhang
```

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/zhang_100_adaptivestepjerk.png" />
</p>
Success! The algorithm counted 105 of Zhang's 100-step trial, with a final SJA of 0.6 m/s^3. We then run the algorithm for a much longer and dynamicaly diverse trial called Decathlon, where Dan walks, stops, and jogs to test the algorithms resilience to a diverse activity set.

```bash
bash$ python sensordata/main.py asjt data/misc/decathalon
```
<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/decathalon_200_adaptivestepjerk.png" />
</p>

Again we can see the Adaptiv adaptive step jerk threshold algorithm is resilient to changes in user and activty as the above trial was 220 steps and Adaptiv calculated 217 individual steps.

###Finally! Adaptiv: The Adaptive Jerk Pace Buffer
In the final iteration of the design we add the two final components of the algorithm, adaptive pace thresholding and step buffers. The thought behind pace threshold is to also include the duration in between steps into step detection. The intuition is that the timer duration between acceleration peak to peak can be just as indicative of a step as the step jerk, which is the peak to trough distance. The same approach taken for dynamically updating the step jerk average is applied for dynamically determining the user's pace time duration. We also implemented a buffer, users can engage in tens of different activities all with different activity signatures. If someone runs for too long, then that could potentially drive the average up. The use of the buffer to determine the average allows for the step calculation to equilibrate after changes in step signatures, pace & step jerk threshold. In the graph below we see how the addition of pace thresholding and buffers improve the step detection. The dashed red line is still the average step jerk while the dashed green line is the average pace duration. 

```bash
bash$ python sensordata/main.py ajpb data/walk/inHand/dan1
```

<p align="center">
  <img src="https://raw.github.com/danielmurray/adaptiv/master/imgs/dan_100_adaptivejerkpacebuffer.png" />
</p>

##Results
Below we can see the results from tests taken from over a handful of different test subjects, phone locations and step detection algorithms. As you can see the Adaptiv method out performs the step detection algorithm implemented on Android devices.

<table class="results-table">
	<tr>
    <th></th>
    <th colspan="2">Peak Acceleration</th>
    <th colspan="2">Step Jerk</th>
    <th colspan="2">Adaptive Step Jerk</th>
    <th colspan="2">Adaptive Step Jerk Pace Buffer</th>
    <th colspan="2">Android</th></tr>
	<tr>
    <th>100 Steps</th>
    <th>Step Avg</th>
    <th>Error</th>
    <th>Step Avg</th>
    <th>Error</th>
    <th>Step Avg</th>
    <th>Error</th>
    <th>Step Avg</th>
    <th>Error</th>
    <th>Step Avg</th>
    <th>Error</th></tr>
	<tr>
    <td align="center">In Hand</td>
    <td align="center">103</td>
    <td align="center">3% </td>
    <td align="center">91</td>
    <td align="center">9% </td>
    <td align="center">98</td>
    <td align="center">2% </td>
    <td align="center">99 </td>
    <td align="center">1%</td>
    <td align="center">102</td>
    <td align="center">2%</td></tr>
	<tr>
    <td align="center">In Pocket</td>
    <td align="center">116</td>
    <td align="center">16%</td>
    <td align="center">80</td>
    <td align="center">20%</td>
    <td align="center">77</td>
    <td align="center">23%</td>
    <td align="center">102</td>
    <td align="center">2%</td>
    <td align="center">106</td>
    <td align="center">6%</td></tr>
	<tr>
    <td align="center">Total    </td>
    <td align="center">109</td>
    <td align="center">9% </td>
    <td align="center">87</td>
    <td align="center">13%</td>
    <td align="center">90</td>
    <td align="center">10%</td>
    <td align="center">100</td>
    <td align="center">0%</td>
    <td align="center">103</td>
    <td align="center">3%</td></tr>
</table>


##Conclusion
Obviously this work is fairly derivate and probably nowhere close to what the actual implementation is in consumer products today. However, I wanted to explored the metrics mobile device accelerometer data, and test out some methods for accurate step detection and accounting. 

