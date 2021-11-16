package com.sala.iotlab.sala_app.bluetooth;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.le.AdvertiseCallback;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertiseSettings;
import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.os.Build;
import android.os.ParcelUuid;
import android.util.Log;

import androidx.annotation.RequiresApi;

import com.sala.iotlab.sala_app.R;
import com.sala.iotlab.sala_app.sala.device.DevicePositionManager;
import com.sala.iotlab.sala_app.sala.device.pdr.SmartPDR;

import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.UUID;

public class BLEManager extends Thread {
    public final UUID uuid = UUID.randomUUID();
    public final ParcelUuid pUuid = new ParcelUuid(uuid);
    public final byte[] uuidByte = getIdAsByte(uuid);
    public final String ipv4;
    public DevicePositionManager devicePos;
    public short seq_num = 1;
    public long timestamp = System.currentTimeMillis();
    private final BluetoothLeAdvertiser advertiser;
    private final AdvertiseCallback advertisingCallback;
    private short angle = 0;  //[j]
    private short y_acc = 0;


    @RequiresApi(api = Build.VERSION_CODES.LOLLIPOP)
    public BLEManager(String ipv4, DevicePositionManager devicePos) {
        this.ipv4 = ipv4;
        this.devicePos = devicePos;
        this.advertiser = BluetoothAdapter.getDefaultAdapter().getBluetoothLeAdvertiser();
        this.advertisingCallback = new AdvertiseCallback() {
            @Override
            public void onStartSuccess(AdvertiseSettings settingsInEffect) {
                super.onStartSuccess(settingsInEffect);
            }
            @Override
            public void onStartFailure(int errorCode) {
                Log.e( "BLE", "Advertising onStartFailure: " + errorCode );
                super.onStartFailure(errorCode);
            }
        };
    }
    public byte[] getIdAsByte(UUID uuid)
    {
        ByteBuffer bb = ByteBuffer.wrap(new byte[16]);
        bb.putLong(uuid.getMostSignificantBits());
        bb.putLong(uuid.getLeastSignificantBits());
        return bb.array();
    }
    @RequiresApi(api = Build.VERSION_CODES.LOLLIPOP)
    public void run() {
        AdvertiseSettings settings = new AdvertiseSettings.Builder()
                .setAdvertiseMode(AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY)
                .setTxPowerLevel( AdvertiseSettings.ADVERTISE_TX_POWER_HIGH )
                .setConnectable( false )
                .build();
        Log.d("debug", "uuid: " + uuid);
        while(true) {
            byte[] beaconMsg = makeBeaconMsg();
            ByteBuffer mManufacturerData = firstData(beaconMsg);

            AdvertiseData data = new AdvertiseData.Builder()
                    .setIncludeDeviceName(false)
                    .addManufacturerData(0x4d, mManufacturerData.array())
                    .build();
            AdvertiseData data2 = new AdvertiseData.Builder()
                    .setIncludeDeviceName(false)
                    .addServiceData(pUuid, Arrays.copyOfRange(beaconMsg, 9, 22))
                    .build();

            advertiser.startAdvertising(settings, data, advertisingCallback);
            try {
                sleep(150);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            advertiser.stopAdvertising(advertisingCallback);
            advertiser.startAdvertising(settings, data2, advertisingCallback);
            try {
                sleep(150);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            advertiser.stopAdvertising(advertisingCallback);
            try {
                sleep(200);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private ByteBuffer firstData(byte[] msg) {
        ByteBuffer mManufacturerData = ByteBuffer.allocate(27);
        mManufacturerData.put((byte)0x02);
        mManufacturerData.put((byte)0x15);

        for (int i=2; i<=17; i++) {
            mManufacturerData.put(uuidByte[i-2]); // adding the UUID
        }
        for(int i =0; i<9; i++) {
            mManufacturerData.put(msg[i]); // first byte of Major
        }

        return mManufacturerData;
    }

    private byte[] makeBeaconMsg() {
        ByteBuffer buffer = ByteBuffer.allocate(22);
        /*  ip address */
        buffer.put(ipv4toByte()).put((byte)',');

        /*  x cor */
        byte[] tmp = new byte[2];
        tmp[0] = (byte)(((short)Math.round(devicePos.getXPos()) >> 8) & 0xff);
        tmp[1] = (byte)((short)Math.round(devicePos.getXPos()) & 0xff);
        buffer.put(tmp).put((byte) ',');

        /*  y cor */
        tmp[0] = (byte)(((short)Math.round(devicePos.getYPos()) >> 8) & 0xff);
        tmp[1] = (byte)((short)Math.round(devicePos.getYPos()) & 0xff);
        buffer.put(tmp).put((byte)',');

        /* angle */
        angle = (short)devicePos.getMSmartPDR().getDeviceAngleInRoom();
        byte[] anglebuf = new byte[2];
        anglebuf[0] = (byte)((angle >> 8) & 0xff);
        anglebuf[1] = (byte)(angle & 0xff);
        buffer.put(anglebuf).put((byte)',');

        /* acceleration */
        y_acc = (short)devicePos.getMSmartPDR().getNowAcc();
        byte[] accelbuf = new byte[2];
        accelbuf[0] = (byte)((y_acc >> 8) & 0xff);
        accelbuf[1] = (byte)(y_acc & 0xff);
        buffer.put(accelbuf).put((byte)'/');

        return buffer.array();
    }

    private byte[] ipv4toByte() {
        Log.d("debug", ipv4);
        String[] ip_tmp = ipv4.split("\\.");
        ByteBuffer tmp = ByteBuffer.allocate(4);
        for(int i =0; i < 4; i++) {
            tmp.put((byte)Integer.parseInt(ip_tmp[i]));
        }
        return tmp.array();
    }

    private byte[] ipv6toByte() {
        ByteBuffer tmp = ByteBuffer.allocate(16);
        //TODO ipv6 to byte array
        return tmp.array();
    }

    @RequiresApi(api = Build.VERSION_CODES.LOLLIPOP)
    public void stopBLE() {
        advertiser.stopAdvertising(advertisingCallback);
    }

}
