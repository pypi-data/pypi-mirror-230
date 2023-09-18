
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo
from typing import Tuple, Set, List
from ordered_set import OrderedSet

from k_lights_interface.k_singleton import KSingletonMeta
from k_lights_interface.k_device import KDevice
from k_lights_interface.k_serial_transport import KSerialTransport
import k_lights_interface.proto_protocol as kprot



class KSerialManager(metaclass=KSingletonMeta):
    def __init__(self):
        self.devices: OrderedSet[KDevice] = OrderedSet([])


    def get_devices_with(self, names: List[str], serial_numbers: List[str]) ->  OrderedSet[KDevice]:
        self.connect_to_all()
        new_set = OrderedSet([])
        if names:
            new_set |= OrderedSet([device for device in self.devices if device.name in names])
        if serial_numbers:
            new_set |=  OrderedSet([device for device in self.devices if device.serial_number in serial_numbers])
        return new_set

    def connect_to_all(self) -> OrderedSet[KDevice]:
        """Connect and initialize KDevice objects for all kelvin serial devices connected to the computer.
        Removes disconnected devices from the device list.

        Returns:
            OrderedSet[KDevice]: A set of KDevice objects
        """
        self.__purge_disconnected_devices()
        possible_ports = self.__get_possible_ports()
        devices_found = OrderedSet([])
        for port in possible_ports:
            ret, name, serial_number = self.__try_get_device_info(port)
            if not ret:
                continue
            k_transport = KSerialTransport(port)
            device = KDevice(name, serial_number, k_transport)
            devices_found.add(device)

        self.devices = self.devices | devices_found
        return self.devices
    
    def __remove_devices_with(self, name:str, serial_number: str):
        self.devices = OrderedSet([device for device in self.devices if device.name != name and device.serial_number != serial_number])

    def __purge_disconnected_devices(self):
        for device in self.devices:
            ret, name = device.get_device_name()
            if not ret:
                self.devices.remove(device)
                print(f"Removed device {name} from device list because it is disconnected.")


    def __try_get_device_info(self, port) -> Tuple[bool, str, str]:
        try:
            with KSerialTransport(port) as k_serial_controller:
                # Setting the receive timeout to short timeout to avoid this process
                # taking a lot of time if there many usb devices connected.
                k_serial_controller.receive_data_timeout_s = 0.2
                did_receive, device_id_message = k_serial_controller.execute_command_with_parsing(kprot.DriverMessage(
                    request=kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_ID)),kprot.DeviceIdMessage, with_response=True,num_tries=1)
                if not did_receive:
                    #print(f"Unable to get device name for device at port {port}")
                    return False, None, None
                #device_id_message = kprot.DeviceIdMessage().FromString(received_data)

                name = device_id_message.name
                did_receive, serial_number_message = k_serial_controller.execute_command_with_parsing(kprot.DriverMessage(
                    request=kprot.RequestMessage(request_type=kprot.RequestTypes.SERIAL_NUMBER)),kprot.SerialNumberMessage, with_response=True,num_tries=1)
                if not did_receive:
                    #print(f"Unable to get serial number for device at port {port}")
                    return False, None, None
                serial_number_hex_string = serial_number_message.data.hex()
                return True, name, serial_number_hex_string
        except Exception as e:
            return False, None, None
        
    

    def __get_possible_ports(self) -> List[ListPortInfo]:
        vid_list = [12259, 0xABCD]
        ports = serial.tools.list_ports.comports(include_links=False)
        valid_ports = [port for port in ports if port.vid in vid_list ]
        return valid_ports
