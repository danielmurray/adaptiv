package com.example.danielmurray.adaptiv.activity;

import android.content.Context;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.location.LocationProvider;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.TextView;

import com.example.danielmurray.adaptiv.GPSListener;
import com.example.danielmurray.adaptiv.MainActivity;
import com.example.danielmurray.adaptiv.R;
import com.example.danielmurray.adaptiv.model.GPSData;
import com.example.danielmurray.adaptiv.utilities.GPSConversion;

import java.util.ArrayList;
import java.util.List;

public class RunningActivity extends ActionBarActivity implements LocationListener {
    private List<GPSData> gpsDatas = new ArrayList<>();
    private List<Double> distances = new ArrayList<>();
    private LocationManager locationManager;
    private boolean collecting;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_running);

        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        collecting = false;
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_running, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onLocationChanged(Location location) {
        setGPSStatus("Connected");

        GPSData data = new GPSData(location.getTime(), location.getLatitude(), location.getLongitude());
        gpsDatas.add(data);

        updateDistance();
        updatePace();
    }

    private void updateDistance() {
        calculateAndAddDistance();

        double totalDistance = sumDistances();
        TextView distanceText = (TextView) findViewById(R.id.distanceText);
        distanceText.setText(String.format("%.2f miles", totalDistance));
    }

    private double sumDistances() {
        double sum = 0;
        for (Double num : distances ) {
            sum += num;
        }
        return sum;
    }

    private double sumDistances(int startIndex, int endIndex) {
        double sum = 0;
        int index = startIndex;
        do {
            sum += distances.get(index);
            index++;
        } while (index != endIndex);
        return sum;
    }

    private void calculateAndAddDistance() {
        if(gpsDatas.size() > 1) {
            GPSData start = gpsDatas.get(gpsDatas.size() - 2);
            GPSData end = gpsDatas.get(gpsDatas.size() - 1);

            double distance = GPSConversion.distance(start.latitude, start.longitude, end.latitude, end.longitude, 'M');
            distances.add(distance);
        }
    }

    private void updatePace() {
        updateCurrentPace();
        updateTotalPace();
    }

    private void updateCurrentPace() {
        if(gpsDatas.size() > 6) {
            GPSData start = gpsDatas.get(gpsDatas.size() - 6);
            GPSData end = gpsDatas.get(gpsDatas.size() - 1);
            long time = end.timestamp - start.timestamp;
            double distance = sumDistances(gpsDatas.size() - 7, gpsDatas.size() - 2);
            double currentPace = time / distance;

            int seconds = (int) Math.round(currentPace / 1000);
            int minutes = seconds / 60;
            seconds = seconds % 60;

            TextView currentPaceText = (TextView) findViewById(R.id.currentPaceText);
            setTime(seconds, minutes, currentPaceText);
        }
    }

    private void setTime(int seconds, int minutes, TextView currentPaceText) {
        currentPaceText.setText(String.format("%d:%02d", minutes, seconds) + " / mile");
    }

    private void updateTotalPace() {
        if(gpsDatas.size() > 1) {
            GPSData start = gpsDatas.get(0);
            GPSData end = gpsDatas.get(gpsDatas.size() - 1);
            long time = end.timestamp - start.timestamp;
            double distance = sumDistances();

            double pace = time / distance;

            int seconds = (int) Math.round(pace / 1000);
            int minutes = seconds / 60;
            seconds = seconds % 60;

            TextView paceText = (TextView) findViewById(R.id.averagePaceText);
            setTime(seconds, minutes, paceText);
        }
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
        if(status == LocationProvider.AVAILABLE) {
            setGPSStatus("Connected");
        } else if (status == LocationProvider.OUT_OF_SERVICE) {
            setGPSStatus("No Connection");
        } else if (status == LocationProvider.TEMPORARILY_UNAVAILABLE) {
            setGPSStatus("No Connection");
        }
    }

    private void setGPSStatus(String s) {
        TextView gps = (TextView) findViewById(R.id.gpsStatusText);
        gps.setText(s);
    }

    @Override
    public void onProviderEnabled(String provider) {

    }

    @Override
    public void onProviderDisabled(String provider) {

    }

    public void startStop(View view){
        if(collecting){
            System.out.println("Stopped collecting");
            collecting = false;

            if(locationManager.getAllProviders().size()!=0) {
                locationManager.removeUpdates(this);
            }
        } else {
            System.out.println("Started collecting");
            collecting = true;
            if(locationManager.getAllProviders().size()!=0) {

                gpsDatas = new ArrayList<>();
                distances = new ArrayList<>();
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000, 2, this);
            }
        }
    }

    public void launchMain(View view) {
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }
}
