# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 12:25:26 2024

@author: jmladeno
"""

import asyncio, struct, sys
from bleak import BleakClient
from pylsl import StreamInfo, StreamOutlet
import numpy as np


CHARACTERISTIC_UUID_BB = "0000fed1-0000-1000-8000-00805f9b34fb" 
#CHANGE ADDRESS, check from scanner.py
ADDRESS = "EA:50:1C:45:3B:08"

# how often we expect to get new data from device (Hz)
SAMPLINGRATE = 12
# length of smoothing window for normalization (seconds)
NORMALIZATION_WINDOW = 20

if __name__ == "__main__":
    
    # StreamInfo(name, type, channel, sampling rate, 'data format', 'UNIQUE ID')
    info = StreamInfo('RSP_raw', 'physio', 1, SAMPLINGRATE, 'float32', 'myuid34234')
    
    # next make an outlet
    outlet = StreamOutlet(info)
    
    buffer = [0] * (SAMPLINGRATE * NORMALIZATION_WINDOW)
        
        
    def notification_handler(sender, data):
        """Simple notification handler which prints the data received."""
        # might get 8 bytes, 4 for red led, 4 for IR led
        if (len(data) >= 4):
            bamp = struct.unpack('>L', data[0:4])[0]

            buffer.append(bamp)
            buffer.pop(0)
            _min = np.min(buffer)
            _max = np.max(buffer)
            normalized_bamp = 0
            if (_min != _max) :
                normalized_bamp = 1. * (bamp - _min) / (_max - _min)
            
            print("Received raw breath value via BLE", bamp, " and sending normalized via LSL:", normalized_bamp)
            outlet.push_sample([normalized_bamp])


    async def main(address, char_uuid):
        async with BleakClient(address) as client:
            print(f"Connected: {client.is_connected}")
            await client.start_notify(char_uuid, notification_handler)
            while True:
                await asyncio.sleep(0)


    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else ADDRESS,
            CHARACTERISTIC_UUID_BB,
        )
    )