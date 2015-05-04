package com.example.danielmurray.adaptiv;

import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationProvider;
import android.os.Bundle;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * Created by rbonick on 4/28/2015.
 */
public class GPSListener implements LocationListener {

    protected final String GPS_FILE_NAME = "gps.csv";

    protected long startTime;
    protected FileIO gpsFile;
    protected MainActivity activity;

    public GPSListener(Context context, MainActivity activity) {
        this.activity = activity;

        startTime = getCurrentTime();

        Date date = new Date();
        String dateString = new SimpleDateFormat("yyyy-MM-dd_hh:mm:ss").format(date);
        String dirName = "/reading_"+dateString+"/";
        gpsFile = new FileIO(dirName, GPS_FILE_NAME, context);
    }

    private long getCurrentTime() {
        return Calendar.getInstance().getTimeInMillis();
    }

    @Override
    public void onLocationChanged(Location location) {
        long timeElapsed = getCurrentTime();
        gpsFile.writeLine(timeElapsed + "," + location.getLatitude() + "," + location.getLongitude());
        activity.setGPSStatus("Connected");
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
        if(status == LocationProvider.AVAILABLE) {
            activity.setGPSStatus("Connected");
        } else if (status == LocationProvider.OUT_OF_SERVICE) {
            activity.setGPSStatus("No Connection");
        } else if (status == LocationProvider.TEMPORARILY_UNAVAILABLE) {
            activity.setGPSStatus("No Connection");
        }
    }

    @Override
    public void onProviderEnabled(String provider) {

    }

    @Override
    public void onProviderDisabled(String provider) {

    }
}
