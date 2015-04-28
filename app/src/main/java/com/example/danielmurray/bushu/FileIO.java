package com.example.danielmurray.bushu;

import java.io.File;
import java.io.IOException;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.BufferedReader;

import android.os.Environment;
import android.content.Context;
import android.util.Log;
import android.media.MediaScannerConnection;
/**
 * Created by danielmurray on 2/22/15.
 */
public class FileIO extends Object{
    private String dirName;
    private String fileName;
    private File d;
    private File f;
    private FileReader fr;
    private BufferedReader br;
    private FileWriter fw;
    private BufferedWriter bw;

    private Context context;

    public FileIO(String dirName, String fileName, Context context){
        this.context = context;

        this.dirName = dirName;
        File d = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS), this.dirName);
        d.mkdirs();

        this.fileName = fileName;
        this.f = new File(d, fileName);

        try{
            if (! this.f.exists() ){
                this.f.createNewFile();
                Log.i("FileIO", "Created "+ this.f.getAbsolutePath());
            }else{
                Log.i("FileIO", "Already Exists "+ this.f.getAbsolutePath());
            }

            this.fw = new FileWriter(this.f);
            this.bw = new BufferedWriter(this.fw);

        }
        catch (IOException e) {
            Log.d("FileIOException", e.toString());
        }
    }

    public void writeLine(String line){

        try{
            this.bw.write(line);
            this.bw.newLine();
        }
        catch (IOException e) {
            Log.d("FileIOException", e.toString());
        }
    }

    public void write(String s){

        try{
            this.bw.write(s);
        }
        catch (IOException e) {
            Log.d("FileIOException", e.toString());
        }
    }

    public void read(){

        try{
            this.fr = new FileReader(this.f);
            this.br = new BufferedReader(this.fr);

            String read;
            StringBuilder builder = new StringBuilder("");

            while((read = this.br.readLine()) != null){
                builder.append(read);
            }

            Log.d("Output", builder.toString());
            this.br.close();
        }
        catch (IOException e) {
            Log.d("FileIOException", e.toString());
        }
    }

    public void close(){

        try{
            Log.i("FileIO", "File Should Be Closed");
            this.bw.close();
        }
        catch (IOException e) {
            Log.d("FileIOException", e.toString());
        }


    }

    public String getAbsolutePath(){
        return this.f.getAbsolutePath();

    }

}
