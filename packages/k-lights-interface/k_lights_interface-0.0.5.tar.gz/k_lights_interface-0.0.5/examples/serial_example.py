from k_lights_interface.k_serial_manager import KSerialManager
from k_lights_interface.k_logging import set_log_level, logging

def example_connect_and_get_power_state():
    set_log_level(logging.INFO)
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    if len(all_connected_devices) == 0:
        print("No devices found")
        return
    device = all_connected_devices[0]
    ret, power_state_msg = device.get_power_state()
    if not ret:
        print("Couldnt read power state")
    print(power_state_msg)




example_connect_and_get_power_state()