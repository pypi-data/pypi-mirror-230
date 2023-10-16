import k_lights_interface.k_device_names as kdn


class KCapabilities:
    def __init__(self, number_of_led_colors=6, minimum_duv=-0.027, maximum_duv=0.027, minimum_kelvin=2000, maximum_kelvin=20000,
                 min_white_point=2800, max_white_point=10000,
                 min_kelvin_gel_mode=2800, max_kelvin_gel_mode=10000,
                 channel_ordering=["lime", "blue", "red", "green", "cyan", "amber"],
                 number_of_fans=0):
        self.number_of_led_colors = number_of_led_colors
        self.minimum_duv = minimum_duv
        self.maximum_duv = maximum_duv
        self.minimum_kelvin = minimum_kelvin
        self.maximum_kelvin = maximum_kelvin
        self.min_white_point = min_white_point
        self.max_white_point = max_white_point
        self.min_kelvin_gel_mode = min_kelvin_gel_mode
        self.max_kelvin_gel_mode = max_kelvin_gel_mode
        self.channel_ordering = channel_ordering
        self.number_of_fans = number_of_fans


k_capabilities = {kdn.play_device_name: KCapabilities(),
                  kdn.play_pro_device_name: KCapabilities(),
                  kdn.epos_300_lamphead_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2),
                  kdn.epos_300_controller_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2),
                  kdn.epos_600_lamphead_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2),
                  kdn.epos_600_controller_device_name: KCapabilities(minimum_kelvin=1700, number_of_fans=2)}
