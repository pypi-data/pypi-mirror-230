from typing import List, Tuple, Union, Set
import numpy as np
import logging
import k_lights_interface.k_device_names as kdn
import k_lights_interface.proto_protocol as kprot
import k_lights_interface.k_capabilities as kcap
from k_lights_interface.k_transport import KTransport

logger = logging.getLogger(__name__)

class KDevice:
    def __init__(self, name, serial_number, k_transport_instance : KTransport):
        self.name = name
        self.serial_number = serial_number
        self.k_transport : KTransport = k_transport_instance
        if self.name in kcap.k_capabilities:
            self.capabilities = kcap.k_capabilities[self.name]
        else:
            logger.info(f"Device {self.name} not in k_capabilities. Need to add it to package.")
            self.capabilities = kcap.KCapabilities()

    # ---------------------------------------------------------------------------- #
    #                      FUNCTIONS CONTROLLING LIGHT OUTPUT                      #
    # ---------------------------------------------------------------------------- #


    def set_intensity(self, intensity: float, output_type: kprot.IntensityMessageLightOutputType, run_light_internal_smoothing=True,  update_light_output=True) -> bool:
        """ Set the intensity of the light.
        Args:
            intensity (float): [0,100]% intensity
            output_type (kprot.IntensityMessageLightOutputType): STABLE = keep light output constant for different mode parameters. 
                                                                 MAXIMUM = always try to output the maximum amount of light limited only by channel saturation or maximum watt draw
            run_light_internal_smoothing (bool, optional): The light will add many intermediate update steps between its current set point and this set point over a certain amount of time (approx 400-600ms). Defaults to True.
            update_light_output (bool, optional): Just recalculate interal values if false. Calculate internal values and emit updated light if true. Defaults to True.
        Returns:
            bool: whether the command was successful
        """
        if intensity < 0 or intensity > 100:
            logger.info(f"Error: Intensity {intensity} out of range [0, 100]")
            return False
        message = kprot.DriverMessage()
        message.intensity = kprot.IntensityMessage(intensity=intensity, light_output_type=output_type,
                                                   smooth_intensity=run_light_internal_smoothing, update_light_output=update_light_output)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret

    def set_cct(self, cct: float, duv: float) -> bool:
        """Sets the CCT and DUV to the given values. Checks that cct and duv are within device specs.

        Args:
            cct (float): correlated color temperature. Minimum is around 1800K-2000K depending on the device, and max is 20KK

            duv (float): -0.027 duv to 0.027 duv. duv is a measure of how far the light is from the black body curve.
              0.027 duv is a very greenish tint, and -0.027 duv is a very pinkish tint.

        Returns:
            bool: whether the command was successful
        """
        if cct < self.capabilities.minimum_kelvin or cct > self.capabilities.maximum_kelvin:
            logger.info(f"Error: CCT {cct} out of range [{self.capabilities.minimum_kelvin}, {self.capabilities.maximum_kelvin}]")
            return False
        if duv < self.capabilities.minimum_duv or duv > self.capabilities.maximum_duv:
            logger.info(f"Error: DUV {duv} out of range [{self.capabilities.minimum_duv}, {self.capabilities.maximum_duv}]")
            return False
        message = kprot.DriverMessage()
        message.cct = kprot.CctMessage(cct=cct, tint=duv)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret
    
    """"""

    def set_xy_cie1931_2nd_degree(self, cie1931_x: float, cie1931_y: float) -> bool:
        """Outputs xy coordinates in CIE1931 2nd degree color space.

        Args:
            cie1931_x (float): x . Valid range depends on the device
            cie1931_y (float): y . Valid range depends on the device

        Returns:
            bool: Whether the command was successful
        """
        message = kprot.DriverMessage()
        message.xy = kprot.XyMessage(x=cie1931_x, y=cie1931_y)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret

    def set_hsi(self, hue: float, saturation: float, intensity: float, color_space: kprot.RgbColorSpace, white_point: float = None):
        """Set hue, saturation and intensity. Can also choose color space. 
        Args:
            hue (float): [0,360] 
            saturation (float): [0,1]
            intensity (float): [0,1]
            color_space (kprot.RgbColorSpace): Choose a color space.
            white_point (float, optional): ONLY VALID FOR DEVICE COLOR SPACE. Can set the white point for the device rgb color space. Defaults to None.
        Returns:
            bool: whether the command was successful 
        """
        if hue < 0 or hue > 360:
            logger.info(f"Error: Hue {hue} out of range [0, 360]")
            return False
        if saturation < 0 or saturation > 1:
            logger.info(f"Error: Saturation {saturation} out of range [0, 1]")
            return False
        if intensity < 0 or intensity > 1:
            logger.info(f"Error: Intensity {intensity} out of range [0, 1]")
            return False
        if white_point:
            if white_point < self.capabilities.min_white_point or white_point > self.capabilities.max_white_point:
                logger.info(
                    f"Error: White point {white_point} out of range [{self.capabilities.min_white_point}, {self.capabilities.max_white_point}]")
                return False
        message = kprot.DriverMessage()
        message.hsi = kprot.HsiMessage(hue=hue, saturation=saturation, intensity=intensity,
                                       color_space=color_space, white_point=white_point)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret

    def set_rgb(self, red: float, green: float, blue: float, color_space: kprot.RgbColorSpace, white_point: float = None) -> bool:
        """Set red, green, blue and color space.  
        Args:
            red (float): [0,255] 
            green (float): [0,255] 
            blue (float): [0,255] 
            color_space (kprot.RgbColorSpace): Choose a color space.
            white_point (float, optional): ONLY VALID FOR DEVICE COLOR SPACE. Can set the white point for the device rgb color space. Defaults to None.
        Returns:
            bool: whether the command was successful 
        """
        if red < 0 or red > 255:
            logger.info(f"Error: Red {red} out of range [0, 255]")
            return False
        if green < 0 or green > 255:
            logger.info(f"Error: Green {green} out of range [0, 255]")
            return False
        if blue < 0 or blue > 255:
            logger.info(f"Error: Blue {blue} out of range [0, 255]")
            return False
        if white_point:
            if white_point < self.capabilities.min_white_point or white_point > self.capabilities.max_white_point:
                logger.info(
                    f"Error: White point {white_point} out of range [{self.capabilities.min_white_point}, {self.capabilities.max_white_point}]")
                return False
        message = kprot.DriverMessage()
        message.rgb = kprot.RgbMessage(red=red, green=green, blue=blue, color_space=color_space, white_point=white_point)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret

    def set_gel(self, brandCategory : kprot.GelBrandCategory, index: int, cct : float) -> bool:
        """Set an onboard gel at the given CCT. This function requires knowledge of the gel library of the device.

        Args:
            brandCategory (kprot.GelBrandCategory): Gel brand and category
            index (int): Choose gel at index in given category. Will clamp to last index in category if higher
            cct (float): The base CCT of the light

        Returns:
            bool: False if the command failed
        """
        if cct < self.capabilities.min_kelvin_gel_mode or cct > self.capabilities.max_kelvin_gel_mode:
            logger.info(f"Error: CCT {cct} out of range [{self.capabilities.min_kelvin_gel_mode}, {self.capabilities.max_kelvin_gel_mode}]")
            return False
        message = kprot.DriverMessage()
        message.gel = kprot.GelSetMessage(brand_category=brandCategory, index=index, cct=cct)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret
    

    def set_effect(self, which_effect: kprot.LightEffectType, play_or_stop: kprot.LightEffectState = None, effect_parameters: kprot.LightEffectParamMessage = None) -> bool:
        if not which_effect and not play_or_stop and not effect_parameters:
            logger.info("Need to provide more information to set effect")
            return False
        message = kprot.DriverMessage()
        message.effect = kprot.LightEffectMessage(which_effect, play_or_stop, effect_parameters)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret


    def set_rgbacl_with_compensation(self,  red: Union[float, List[float]], green: float = None, blue: float = None, 
                                 amber: float = None, cyan: float = None, lime: float = None) -> bool:
        """sets the channels to the given values with compensation for temperature, drift and non-linearities in the drivers.

        Args:
            red (Union[float, List[float]]): If this is a list, it should contain six integers representing 
            red, green, blue, amber, cyan, and lime, in that order. If it's an float, the other 
            arguments should also be floats representing the colors.
            green (float, optional): . Defaults to None.
            blue (float, optional): . Defaults to None.
            amber (float, optional): . Defaults to None.
            cyan (float, optional): . Defaults to None.
            lime (float, optional): . Defaults to None.
        """

        if isinstance(red, list) and len(red) == 6:
                red, green, blue, amber, cyan, lime = red
        elif not all([green, blue, amber, cyan, lime]):
            raise ValueError("Please provide all color values either as separate arguments or as a list")
        message = kprot.DriverMessage()
        message.rgbacl = kprot.RgbaclMessage(red=red, green=green, blue=blue, amber=amber, cyan=cyan, lime=lime)
        ret, _ = self.k_transport.execute_command(message, with_response=True)
        return ret

    def set_rgbacl_emitter_channels_without_compensation_safe(self,  red: Union[float, List[float]], green: float = None, blue: float = None, 
                                 amber: float = None, cyan: float = None, lime: float = None) -> bool:
        """Sets the channels to the given values with maximum watt draw verification.

        Args:
            red (Union[float, List[float]]): If this is a list, it should contain six integers representing 
            red, green, blue, amber, cyan, and lime, in that order. If it's an float, the other 
            arguments should also be floats representing the colors.
            green (float, optional): . Defaults to None.
            blue (float, optional): . Defaults to None.
            amber (float, optional): . Defaults to None.
            cyan (float, optional): . Defaults to None.
            lime (float, optional): . Defaults to None.
        """
        return self.__set_rgbacl_emitter_channels(red, green, blue, amber, cyan, lime, verify_outputs=True)

    def set_rgbacl_emitter_channels_without_compensation_unsafe(self, red: Union[float, List[float]], green: float = None, blue: float = None, 
                                 amber: float = None, cyan: float = None, lime: float = None) -> bool:
        """Sets the channels to the given values without verifying that the outputs are within the maximum watt draw of the device.
            Please only use this if you know what you are doing. You will damage the device if you make it draw too much power.
            This is normally only used for testing purposes, calibration and other special cases.
            
        Args:
            red (Union[float, List[float]]): If this is a list, it should contain six integers representing 
            red, green, blue, amber, cyan, and lime, in that order. If it's an float, the other 
            arguments should also be floats representing the colors.
            green (float, optional): . Defaults to None.
            blue (float, optional): . Defaults to None.
            amber (float, optional): . Defaults to None.
            cyan (float, optional): . Defaults to None.
            lime (float, optional): . Defaults to None.
        """
        return self.__set_rgbacl_emitter_channels(red, green, blue, amber, cyan, lime, verify_outputs=False)


# ---------------------------------------------------------------------------- #
#                       FUNCTIONS FOR GETTING DATA FROM A DEVICE               #
# ---------------------------------------------------------------------------- #

    def get_device_name(self) -> Tuple[bool, str]:
        """Get the name of the device.

        Returns:
            bool,str: Valid message if bool is True
        """
        message = kprot.DriverMessage()
        message.request = kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_ID)
        ret, device_id_message = self.k_transport.execute_command_with_parsing(message, kprot.DeviceIdMessage, with_response=True)
        if not ret:
            return False, None
        return True, device_id_message.name

    def get_device_stats(self) -> Tuple[bool, kprot.DeviceStatsMessage]:
        """Get device stats. Look at DeviceStatsMessage for more info.

        Returns:
            bool,kprot.DeviceStatsMessage: Valid message if bool is True
        """
        message = kprot.DriverMessage()
        message.request = kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_STATS)
        ret, device_stats_message = self.k_transport.execute_command_with_parsing(message,kprot.DeviceStatsMessage, with_response=True)
        if not ret:
            return False, None
        return True, device_stats_message

    def get_emitter_temperature(self) -> Tuple[bool, float]:
        """Get the temperature of the emitter in degrees celsius IF the device has emitter temperature.

        Returns:
            bool,float: Valid message if bool is True
        """
        ret, message = self.get_device_temperatures()
        if hasattr(message, 'emitter_temperature'):
            return True, message.emitter_temperature
        else:
            return False, None

    def get_device_temperatures(self) -> Tuple[bool, Union[kprot.PlayPowerStateMessage,
                                                           kprot.Epos300ControllerTemperaturesMessage,
                                                           kprot.Epos300LampheadTemperaturesMessage,
                                                           kprot.Epos600ControllerTemperaturesMessage,
                                                           kprot.Epos600LampheadTemperaturesMessage]]:
        """Get temperatures of the device.

        Returns:
            Tuple[bool, Union[kprot.PlayPowerStateMessage, kprot.Epos300ControllerTemperaturesMessage, kprot.Epos300LampheadTemperaturesMessage, kprot.Epos600ControllerTemperaturesMessage, kprot.Epos600LampheadTemperaturesMessage]]: _description_
        """
        message = kprot.DriverMessage()
        message.request = kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_TEMPERATURES)
        ret, rx_msg = self.k_transport.execute_command_with_parsing(message,kprot.DeviceTemperaturesMessage, with_response=True)
        if not ret:
            return False, None
        if rx_msg.epos300_lamphead_temperatures_message:
            return True, rx_msg.epos300_lamphead_temperatures_message
        elif rx_msg.epos300_controller_temperatures_message:
            return True, rx_msg.epos300_controller_temperatures_message
        elif rx_msg.epos600_lamphead_temperatures_message:
            return True, rx_msg.epos600_lamphead_temperatures_message
        elif rx_msg.epos600_controller_temperatures_message:
            return True, rx_msg.epos600_controller_temperatures_message
        elif rx_msg.play_temperatures_message:
            return True, rx_msg.play_temperatures_message
        else:
            return False, None
        

    def get_current_light_output_data(self) -> Tuple[bool, kprot.CurrentLightOutputMessage]:
        """Get data on the current light output on the light. Look at the CurrentLightOutputMessage for more info.

        Returns:
           bool,kprot.CurrentLightOutputMessage : Valid message if bool is True
        """
        message = kprot.DriverMessage()
        message.request = kprot.RequestMessage(request_type=kprot.RequestTypes.CURRENT_LIGHT_OUTPUT)
        ret, current_light_output_message = self.k_transport.execute_command_with_parsing(message, kprot.CurrentLightOutputMessage, with_response=True)
        if not ret:
            return False, None
        return True, current_light_output_message

    def get_power_state(self) -> Tuple[bool, Union[kprot.PlayPowerStateMessage,kprot.Epos300PowerStateMessage]]:
        """Get the power state of the device. Epos 600 not implemented yet.

        Returns:
            Tuple[bool, Union[kprot.PlayPowerStateMessage,kprot.Epos300PowerStateMessage]]: _description_
        """
        message = kprot.DriverMessage()
        message.request = kprot.RequestMessage(request_type=kprot.RequestTypes.POWER_STATE)
        ret, rx_msg = self.k_transport.execute_command_with_parsing(message,kprot.PowerStateMessage, with_response=True)
        if not ret:
            return False, None
        if rx_msg.play_power_state_message:
            return True, rx_msg.play_power_state_message
        elif rx_msg.epos300_power_state_message:
            return True, rx_msg.epos300_power_state_message
        else:
            return False, None
            
    def __set_rgbacl_emitter_channels(self,red: Union[float, List[float]], green: float = None, blue: float = None, 
                                 amber: float = None, cyan: float = None, lime: float = None,  verify_outputs: bool = True) -> bool:
        if isinstance(red, list) and len(red) == 6:
            red, green, blue, amber, cyan, lime = red
        elif not all([green, blue, amber, cyan, lime]):
            raise ValueError("Please provide all color values either as separate arguments or as a list")
        values = self.__rgbacl_to_device_list(red, green, blue, amber, cyan, lime)
        channel_message = kprot.DriverMessage()
        channel_message.set_emitter_channels = kprot.SetEmitterChannelsMessage(output_value=values, verify_outputs=verify_outputs)
        ret, _ = self.k_transport.execute_command(channel_message, with_response=True)
        return ret

    def __rgbacl_to_device_list(self, red, green, blue, amber, cyan, lime) -> List[float]:
        if len(self.capabilities.channel_ordering) != 6:
            logger.info("Device does not have 6 channels. Cant use rgbacl functions")
            return []
        channel_list = [0]*6
        channel_list[self.capabilities.channel_ordering.index("red")] = red
        channel_list[self.capabilities.channel_ordering.index("green")] = green
        channel_list[self.capabilities.channel_ordering.index("blue")] = blue
        channel_list[self.capabilities.channel_ordering.index("amber")] = amber
        channel_list[self.capabilities.channel_ordering.index("cyan")] = cyan
        channel_list[self.capabilities.channel_ordering.index("lime")] = lime
        return channel_list

    def __str__(self):
        return f"Device: {self.name} , Serial nr: {self.serial_number}, Transport: {self.k_transport.get_transport_type()}"


    def __hash__(self):
        return hash((self.name, self.serial_number))
    
    def __eq__(self, other):
        if isinstance(other, KDevice):
            return self.name == other.name and self.serial_number == other.serial_number
        return False
