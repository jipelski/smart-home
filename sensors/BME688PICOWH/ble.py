# The MIT License (MIT)
#
# Copyright (c) 2024 Claudiu Florin Jipa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import struct
import time
import ubluetooth

def advertising_payload(name=None, services=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.append(len(value) + 1)
        payload.append(adv_type)
        payload.extend(value)

    if name:
        _append(0x09, name.encode('utf-8'))

    if services:
        for uuid in services:
            _append(0x03, struct.pack("<h", uuid))

    return payload

class BLEPeripheral:
    def __init__(self, name="PicoW_BLE"):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.name = name
        self.connected = False
        
        self.last_response_time = time.time()
        self.timeout = 30
        
        self.ble.irq(self.irq)
        
        self.service_uuid = ubluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
        
        self.env_data_uuid = ubluetooth.UUID("12345678-1234-5678-1234-56789abcdef5")
        
        self.client_ping_uuid = ubluetooth.UUID("87654321-4321-8765-4321-abcdef123456")
        
        self.env_data_char = (self.env_data_uuid, ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY)
        self.client_ping_char = (self.client_ping_uuid, ubluetooth.FLAG_WRITE)
        
        self.service = (self.service_uuid, (self.env_data_char,))
        self.services = (self.service,)
        ((self.env_data_handle,),) = self.ble.gatts_register_services(self.services)
        
        self.advertise()

    def irq(self, event, data):
        if event == 1:
            self.connected = True
            conn_handle, _, _ = data
            self.conn_handle = conn_handle
        elif event == 2:
            self.connected = False
            conn_handle, _, _ = data
            print(f"Central disconnected, handle: {conn_handle}")
            self.advertise()  # Restart advertising after disconnection
        elif event == 3:
            conn_handle, attr_handle = data
            if attr_handle == self.client_ping_handle:
                self.last_response_time = time.time()

    def advertise(self):
        try:
            self.stop_advertise()
            name = bytes(self.name, 'utf-8')
            adv_data = advertising_payload(name=self.name)
            self.ble.gap_advertise(1000, adv_data)
            print("Advertising environmental service...")
        except Exception as e:
            print("Error during advertising:", e)
    
    def handle_timeout(self):
        print(f"No ping from client for {self.timeout} seconds, restarting advertising.")
        self.connected = False
        self.stop_advertise()
        self.advertise()

    def stop_advertise(self):
        """Stop any current advertising before restarting."""
        try:
            self.ble.gap_advertise(None)
            print("Stopped advertising.")
        except Exception as e:
            print("Error stopping advertising (may not have been advertising):", e)

    def send_env_data(self, time_t, temperature, humidity, pressure, gas):
        if self.connected:
            payload = struct.pack(
                'hbbbbbffff', 
                time_t[0], 
                time_t[1], 
                time_t[2], 
                time_t[4], 
                time_t[5], 
                time_t[6], 
                temperature, 
                humidity, 
                pressure, 
                gas)
            try:
                self.ble.gatts_write(self.env_data_handle, payload)
                self.ble.gatts_notify(self.conn_handle, self.env_data_handle)
            except Exception as e:
                print(f"Error during notification: {e}")
                self.handle_timeout()
            print("Notification sent with environmental data.")
            
        else:
            print("No connected clients, cannot send notification.")
