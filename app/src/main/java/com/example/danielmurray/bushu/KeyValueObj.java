package com.example.danielmurray.bushu;

/**
 * Created by danielmurray on 2/20/15.
 */

public class KeyValueObj extends Object{
    private String key;
    private String value;

    public KeyValueObj(String key, String value){
        this.key = key;
        this.value = value;
    }

    public String getKey(){
        return this.key;
    }

    public String getValue(){
        return this.value;
    }

    public void setValue(String value){
        this.value = value;
    }
}