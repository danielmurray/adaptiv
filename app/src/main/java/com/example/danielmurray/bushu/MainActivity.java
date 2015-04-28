package com.example.danielmurray.bushu;

import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.Date;

import android.app.Activity;
import android.content.Context;
import android.hardware.*;
import android.os.Bundle;
import android.os.Environment;
import android.widget.ListView;
import android.widget.Button;
import android.util.Log;
import android.view.View;

import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity implements SensorEventListener {

    private KeyValueObj xObj = new KeyValueObj("X","0");
    private KeyValueObj yObj = new KeyValueObj("Y","10");
    private KeyValueObj zObj = new KeyValueObj("Z","100");
    private KeyValueObj ourStepObj = new KeyValueObj("Our Steps","10000");

    private ArrayList<KeyValueObj> keyValueObjList = new ArrayList<KeyValueObj>(Arrays.asList(new KeyValueObj[]{
            xObj,
            yObj,
            zObj,
            ourStepObj
    }));

    private KeyValueAdapter adapter;

    private ListView listView;
    private Button button;

    private Context context;

    private SensorManager sensorManager;

    private boolean collecting = false;

    private FileIO accelFile;
    private FileIO gyroFile;
    private FileIO laFile;
    private FileIO gravFile;
    private FileIO stepFile;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Get an instance of the SensorManager
        sensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);

        if(sensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER).size()!=0){
            Sensor accel = sensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER).get(0);
            sensorManager.registerListener(this,accel, SensorManager.SENSOR_DELAY_GAME);
        }

        if(sensorManager.getSensorList(Sensor.TYPE_GYROSCOPE).size()!=0){
            Sensor gyro = sensorManager.getSensorList(Sensor.TYPE_GYROSCOPE).get(0);
            sensorManager.registerListener(this,gyro, SensorManager.SENSOR_DELAY_GAME);
        }

        if(sensorManager.getSensorList(Sensor.TYPE_LINEAR_ACCELERATION).size()!=0){
            Sensor la = sensorManager.getSensorList(Sensor.TYPE_LINEAR_ACCELERATION).get(0);
            sensorManager.registerListener(this, la, SensorManager.SENSOR_DELAY_GAME);
        }

        if(sensorManager.getSensorList(Sensor.TYPE_GRAVITY).size()!=0){
            Sensor grav = sensorManager.getSensorList(Sensor.TYPE_GRAVITY).get(0);
            sensorManager.registerListener(this, grav, SensorManager.SENSOR_DELAY_GAME);
        }

        if(sensorManager.getSensorList(Sensor.TYPE_STEP_COUNTER).size()!=0){
            Sensor step = sensorManager.getSensorList(Sensor.TYPE_STEP_COUNTER).get(0);
            sensorManager.registerListener(this, step, SensorManager.SENSOR_DELAY_GAME);
        }

        context = getApplicationContext();

        listView = (ListView) findViewById(R.id.data_list);
        button = (Button) findViewById(R.id.button);

        adapter = new KeyValueAdapter(this, keyValueObjList);

        listView.setAdapter(adapter);

        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if(collecting){
                    //End data stream to CSV file
                    collecting = false;
                    button.setText("New Capture");

                    accelFile.close();
                    gyroFile.close();
                    laFile.close();
                    gravFile.close();
                    stepFile.close();

                }else{
                    //Begin data stream to CSV file
                    collecting = true;

                    Date date = new Date();
                    String dateString = new SimpleDateFormat("yyyy-MM-dd_hh:mm:ss").format(date);
                    String dirName = "/reading_"+dateString+"/";
                    String aFileName = "accelerometer.csv";
                    String gFileName = "gyroscope.csv";
                    String lFileName = "linearAccelerometer.csv";
                    String grFileName = "gravity.csv";
                    String sFileName = "step.csv";

                    button.setText("End Capture "+ dateString);

                    accelFile = new FileIO(dirName, aFileName, context);
                    gyroFile = new FileIO(dirName, gFileName, context);
                    laFile = new FileIO(dirName, lFileName, context);
                    gravFile = new FileIO(dirName, grFileName, context);
                    stepFile = new FileIO(dirName, sFileName, context);

                }
            }
        });

    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER){
            double x = event.values[0];
            double y = event.values[1];
            double z = event.values[2];

            xObj.setValue(String.valueOf(x));
            yObj.setValue(String.valueOf(y));
            zObj.setValue(String.valueOf(z));

            adapter.notifyDataSetChanged();

            if(collecting){
                String line = String.valueOf(event.timestamp) + ',' + x + ',' + y + ',' + z;
                accelFile.writeLine(line);
            }

        }else if(event.sensor.getType() == Sensor.TYPE_GYROSCOPE){
            double x = event.values[0];
            double y = event.values[1];
            double z = event.values[2];

            if(collecting){
                String line = String.valueOf(event.timestamp) + ',' + x + ',' + y + ',' + z;
                gyroFile.writeLine(line);
            }

        }else if(event.sensor.getType() == Sensor.TYPE_LINEAR_ACCELERATION){
            double x = event.values[0];
            double y = event.values[1];
            double z = event.values[2];

            if(collecting){
                String line = String.valueOf(event.timestamp) + ',' + x + ',' + y + ',' + z;
                laFile.writeLine(line);
            }

        }else if(event.sensor.getType() == Sensor.TYPE_STEP_COUNTER){
            double steps = event.values[0];

            ourStepObj.setValue(String.valueOf(steps));
            adapter.notifyDataSetChanged();

            if(collecting){
                String line = String.valueOf(event.timestamp) + ',' + steps;
                stepFile.writeLine(line);
            }
        }else if(event.sensor.getType() == Sensor.TYPE_GRAVITY){
            double x = event.values[0];
            double y = event.values[1];
            double z = event.values[2];

            if(collecting){
                String line = String.valueOf(event.timestamp) + ',' + x + ',' + y + ',' + z;
                gravFile.writeLine(line);
            }
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // TODO Auto-generated method stub
    }
}
