package com.example.danielmurray.bushu;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.ArrayList;

/**
 * Created by danielmurray on 2/20/15.
 */

public class KeyValueAdapter extends ArrayAdapter<KeyValueObj> {

    public KeyValueAdapter(Context context,ArrayList<KeyValueObj> objects) {
        super(context, 0, objects);
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        // Get the data item for this position
        KeyValueObj kvo = getItem(position);

        // Check if an existing view is being reused, otherwise inflate the view
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.data_list_item, parent, false);
        }
        // Lookup view for data population
        TextView key = (TextView) convertView.findViewById(R.id.key);
        TextView value = (TextView) convertView.findViewById(R.id.value);
        // Populate the data into the template view using the data object
        key.setText(kvo.getKey());
        value.setText(kvo.getValue());
        // Return the completed view to render on screen
        return convertView;
    }

}