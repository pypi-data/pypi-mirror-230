
import asyncio
import logging

from typing import Set, Tuple
from ordered_set import OrderedSet
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from k_lights_interface.k_ble_transport import KBleTransport, UART_SERVICE_UUID, UART_TX_CHAR_UUID, UART_RX_CHAR_UUID
from k_lights_interface.k_singleton import KSingletonMeta
from k_lights_interface.k_device import KDevice
import k_lights_interface.k_device_names as kdn
import k_lights_interface.proto_protocol as kprot


logger = logging.getLogger(__name__)


class KAdvertisingInfo:
    def __init__(self, name, mac_address,device :BLEDevice,  adv_data : AdvertisementData):
        self.name = name
        self.mac_address = mac_address
        self.last_received_adv_data = adv_data
        self.last_received_ble_device = device

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, KAdvertisingInfo):
            return self.mac_address == __value.mac_address
        return False
    def __hash__(self) -> int:
        return hash(self.mac_address)
    
    def __str__(self):
        return f"{self.name} {self.mac_address}"

class KBleManager(metaclass=KSingletonMeta):
    def __init__(self):
        self.__ble_lock = asyncio.Lock()
        self.__k_devices: OrderedSet[KDevice] = OrderedSet([])
        self.__scanner = BleakScanner(self.__advertising_callback,[UART_SERVICE_UUID])
        self.__accumulated_advertising_info = OrderedSet([])



    async def connect_to_all(self, scan_duration_s : float = 5) -> OrderedSet[KDevice]:
        await self.scan(scan_duration_s)
        for k_adv_info in self.__accumulated_advertising_info:
            connected_device = await self.connect_to_device_with_tries(k_adv_info)
            if connected_device:
                self.__k_devices.add(connected_device)
        return self.__k_devices

    async def scan(self, scan_duration_s : float) -> OrderedSet[KAdvertisingInfo]:
        async with self.__ble_lock:
            self.__accumulated_advertising_info.clear()
            await self.__scanner.start()
            await asyncio.sleep(scan_duration_s)
            await self.__scanner.stop()
            logger.info(f"Finished scanning. Found {len(self.__accumulated_advertising_info)} devices")
            for k_adv_info in self.__accumulated_advertising_info:
                logger.info(f"Found {k_adv_info}")
            return self.__accumulated_advertising_info

    async def connect_to_device_with_tries(self, k_adv_info : KAdvertisingInfo, num_tries : int = 3) -> KDevice:
        for i in range(num_tries):
            k_device = await self.connect_to_device(k_adv_info)
            if k_device:
                return k_device
        return None

    async def connect_to_device(self, k_adv_info : KAdvertisingInfo) -> KDevice:
        if self.__has_k_device_for_adv_info(k_adv_info):
            logger.info(f"{k_adv_info} is already in device list")
            return None
        device = k_adv_info.last_received_ble_device

        k_ble_transport = KBleTransport()
        k_ble_transport.init(self.__ble_lock, device)
        did_connect = await k_ble_transport.try_connect()
        if not did_connect:
            logger.error(f"Could not connect to {device.address}")
            return None
        logger.info(f"Connected to {device.address}")
        ret, name, serial_number_hex_string = await self.__try_get_device_info(k_ble_transport)
        if not ret:
            logger.error(f"Could not get device info from {device.address}")
            return None
        k_device = KDevice(name, serial_number_hex_string, k_ble_transport)
        return k_device

    async def __try_get_device_info(self, k_ble_transport : KBleTransport) -> Tuple[bool, str, str]:
        try:
            did_receive, device_id_message = await k_ble_transport.execute_command_with_parsing_async(kprot.DriverMessage(
                request=kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_ID)),kprot.DeviceIdMessage, with_response=True,num_tries=1)
            if not did_receive:
                return False, None, None
            name = device_id_message.name
            did_receive, serial_number_message = await k_ble_transport.execute_command_with_parsing_async(kprot.DriverMessage(
                request=kprot.RequestMessage(request_type=kprot.RequestTypes.SERIAL_NUMBER)),kprot.SerialNumberMessage, with_response=True,num_tries=1)
            if not did_receive:
                return False, None, None
            serial_number_hex_string = serial_number_message.data.hex()
            return True, name, serial_number_hex_string
        except Exception as e:
            return False, None, None
        
    def __has_k_device_for_adv_info(self, k_adv_info : KAdvertisingInfo) -> bool:
        return any([connected_device.k_transport.get_mac_addr() == k_adv_info.mac_address for connected_device in self.__k_devices])


    def __advertising_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        if device.name in kdn.valid_btle_adv_names:
            logger.info("%s: %r", device.address, advertisement_data)
            index = self.__accumulated_advertising_info.add(KAdvertisingInfo(device.name, device.address,device, advertisement_data))
            self.__accumulated_advertising_info[index].last_received_adv_data = advertisement_data
            self.__accumulated_advertising_info[index].last_received_ble_device = device

