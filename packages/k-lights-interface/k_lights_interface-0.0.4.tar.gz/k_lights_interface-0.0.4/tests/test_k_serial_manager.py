

def test_connect_using_name():
    ## Test expects one kelvin device connected using usb
    from k_lights_interface.k_serial_manager import KSerialManager
    import k_lights_interface.k_device_names as kdn
    dev_manager = KSerialManager()

    all_connected_devices = dev_manager.connect_to_all()
    assert(len(all_connected_devices) == 1)
    light_name = all_connected_devices[0].name
    serial_number = all_connected_devices[0].serial_number
    all_connected_devices = dev_manager.get_devices_with(None,None)
    assert(len(all_connected_devices) == 0)
    all_connected_devices = dev_manager.get_devices_with(None,[serial_number])
    assert(len(all_connected_devices) > 0)
    all_connected_devices = dev_manager.get_devices_with([light_name],[serial_number])
    assert(len(all_connected_devices) > 0)
    