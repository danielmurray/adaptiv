package com.example.danielmurray.bushu;

import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
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

    public GPSListener(Context context) {
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
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {

    }

    @Override
    public void onProviderEnabled(String provider) {

    }

    @Override
    public void onProviderDisabled(String provider) {

    }
}
