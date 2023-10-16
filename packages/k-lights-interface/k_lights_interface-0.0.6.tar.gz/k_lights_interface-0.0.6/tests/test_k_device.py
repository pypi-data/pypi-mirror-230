


from time import sleep


def test_k_device():
    ## Test expects one kelvin device connected using usb
    from k_lights_interface.k_serial_manager import KSerialManager
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    [print(dev) for dev in all_connected_devices]

    device = all_connected_devices.pop()
    print(f"Chosen device for tests: {device}")

    ret, temp = device.get_emitter_temperature()
    assert(ret == True)
    ret, device_stats = device.get_device_stats()
    assert(ret == True)
    ret, device_id = device.get_device_name()
    assert(ret == True)

def test_set_channels():
    from k_lights_interface.k_serial_manager import KSerialManager
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    [print(dev) for dev in all_connected_devices]

    device = all_connected_devices.pop()
    print(f"Chosen device for tests: {device}")
    for i in range(6):
        test_list = [0]*6
        test_list[i] = 10
        device.set_rgbacl_emitter_channels_without_compensation_unsafe(test_list)
        sleep(0.4)
    sleep(0.4) 
    device.set_rgbacl_emitter_channels_without_compensation_unsafe([0,0,0,0,0,0])

