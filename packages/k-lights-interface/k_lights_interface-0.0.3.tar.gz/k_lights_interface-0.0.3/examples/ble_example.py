import asyncio
from k_lights_interface.k_ble_manager import KBleManager


async def main():
    ble_manager = KBleManager()
    devices = await ble_manager.connect_to_all()
    if len(devices) == 0:
        print("No devices found")
        return
    print(devices)
    ret, device_stats = devices[0].get_device_stats()
    print(device_stats)


if __name__ == "__main__":
    asyncio.run(main())
    print("finished")
