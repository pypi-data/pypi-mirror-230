# Kelvin lights interface 


## Installation

Public install. Some parts of the communication interface which are closely tied to Kelvins ip is removed.

     pip install k-lights-interface

Private install

     Use Look at private_access_key.md

## Features

- Control Kelvin devices. Set brightness, CCT and Duv, RGB, HSI, and more. Read out temperatures, voltages, and more. 
- Supports Serial communication using pyserial package
- Supports BLE communication using bleak package. Check bleak for requirements. Bleak must also be installed separately, f.ex pip install bleak


## Usage
### Serial usage:

To get a device to control:
```python
from k_lights_interface.k_serial_manager import KSerialManager

dev_manager = KSerialManager()
alldevs = dev_manager.get_all_devices()
[print(dev) for dev in alldevs]
```




## Running tests
Ensure workspace at root

     pytest
     

## Updating protocol buffers file

Ensure at workspace root

Run this to generate the proto files for internal use
     
     python -m grpc_tools.protoc -I raw_proto/ --python_betterproto_out=src/k_lights_interface/ k_full.proto

Run this to generate the proto files for public use

     python -m grpc_tools.protoc -I raw_proto/ --python_betterproto_out=src/k_lights_interface/ k_public.proto
