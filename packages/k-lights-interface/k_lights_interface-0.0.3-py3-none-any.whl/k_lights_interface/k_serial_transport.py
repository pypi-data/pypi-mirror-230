import timeit
from typing import Tuple
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo
import serial.tools.list_ports
import yahdlc
from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    FRAME_NACK,
    FCSError,
    MessageError,
    frame_data,
    get_data,
)
import k_lights_interface.proto_protocol as light_protocol
from k_lights_interface.k_transport import KTransport


class KSerialTransport(KTransport):
    port_info : ListPortInfo = None
    serial_port: serial.Serial = None
    sequence_number = 0
    last_ack_sequence_number = 0
    receive_data_timeout_s = 2


    def __init__(self, port_info: ListPortInfo):
        self.port_info = port_info
        self.serial_port = Serial(self.port_info.device)

    def try_connect(self, force_reconnect: bool) -> bool:
        try:
            if force_reconnect:        
                self.serial_port.close()
                self.serial_port.open()
                return True
            if self.serial_port is None:
                self.serial_port = Serial(self.port_info.device)
            elif self.serial_port.is_open is False:
                self.serial_port.open()
            return True
        except Exception as e:
            return False


    def get_transport_type(self) -> str:
        return "serial"
    
    def get_mac_addr(self) -> str:
        return ""
    
    def try_reconnect(self) -> bool:

        return True
    
    def is_connected(self) -> bool:
        return True
    
    def clear_sequence_number(self):
        self.sequence_number = 0
        self.last_ack_sequence_number = 0

    def send_data(self, bytes_data, seq_no):
        frame = yahdlc.frame_data(bytes_data, yahdlc.FRAME_DATA, seq_no)
        self.serial_port.write(frame)

    def got_ack_on_command(self) -> bool:
        return self.sequence_number == (self.last_ack_sequence_number - 1)

    def receive_data(self) -> Tuple[bool, bytearray]:
        try:
            start_time = timeit.default_timer()
            received_bytes = bytearray()
            received_frame = None
            while (not self.got_ack_on_command()):
                received_bytes = bytearray()
                if (timeit.default_timer() - start_time) > self.receive_data_timeout_s:
                    return False, bytearray()
                bytes_to_read = self.serial_port.in_waiting
                if bytes_to_read > 0:
                    received_bytes.extend(self.serial_port.read(bytes_to_read))
                try:
                    data, data_type, seq_no = yahdlc.get_data(bytes(received_bytes))
                    if data_type == yahdlc.FRAME_DATA:
                        received_frame = bytearray(data)
                    elif data_type == yahdlc.FRAME_ACK:
                        self.last_ack_sequence_number = seq_no
                    elif data_type == yahdlc.FRAME_NACK:
                        return False, bytearray()
                    return True, received_frame
                except MessageError:
                    # No HDLC frame detected.
                    # print("No HDLC frame detected")
                    continue
                except FCSError:
                    print("FCS error")
                    continue
                except Exception as e:
                    # Unable to parse received bytes
                    continue
            return False, bytearray()
        except Exception as e:
            print("exception in receive_data")
            return False, bytearray()

    def execute_command_with_parsing(self, message: light_protocol.DriverMessage, parsing_object, with_response: bool = True, num_tries=3) -> Tuple[bool, bytearray]:
        ret, rx_data = self.execute_command(message, with_response, num_tries)
        if not ret or not rx_data or len(rx_data) == 0:
            return False, None
        try:
            parsing_instance = parsing_object()
            return True, parsing_instance.FromString(rx_data)
        except Exception as e:
            print(f"Exception in execute_command_with_parsing: {e}")
            return False, None



    def execute_command(self, message: light_protocol.DriverMessage, with_response: bool = True, num_tries=3) -> Tuple[bool, bytearray]:
        for i in range(num_tries):
            try:
                ret, bytes_data = self.__execute_command_once(message, with_response)
                if ret:
                    return True, bytes_data
            except Exception as e:
                print(f"Exception in execute_command: {e}")
                print("Attempting to reconnect once and adding a retry attempt")
                self.try_connect(force_reconnect=True)
                ret, bytes_data = self.__execute_command_once(message, with_response)
                if ret:
                    return True, bytes_data

        return False, bytearray()

    def __execute_command_once(self, message: light_protocol.DriverMessage, with_response: bool = True) -> Tuple[bool, bytearray]:
        has_connection = self.try_connect(force_reconnect=False)
        if not has_connection:
            return False, bytearray()
        self.clear_sequence_number()
        self.serial_port.read_all()
        self.send_data(message.SerializeToString(), self.sequence_number)
        if with_response:
            did_receive, received_data = self.receive_data()
            if not did_receive:
                #print("Unable to receive data from light")
                return False, bytearray()
            return True, received_data
        return True, bytearray()

    def __del__(self):
        try:
            self.serial_port.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.serial_port.close()
        except:
            pass
