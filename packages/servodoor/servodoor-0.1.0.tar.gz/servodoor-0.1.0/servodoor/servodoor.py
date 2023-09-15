import sys
import json
import serial

class ServoDoor(serial.Serial):

    NUM_THROW_AWAY_ON_INIT = 10

    def __init__(self, port):
        self.port_param = {'port': port, 'baudrate': 115200, 'timeout': 2.0}
        super().__init__(**self.port_param)
        self.throw_away_lines()

    def throw_away_lines(self):
        """ 
        Throw away first few lines. Called on initialization to deal with case
        where user has updated the firmware (or similar) and it has written a
        bunch text to the serial port. 
        """
        self.timeout = 0.1
        for i in range(self.NUM_THROW_AWAY_ON_INIT):
            line = self.readline()
        self.timeout = self.port_param['timeout']

    def send_and_receive(self, msg_dict):
        """
        Send a message and receive a response from the the device.
        """
        msg_json = f'{json.dumps(msg_dict)}\n'
        msg_json = msg_json.encode()
        self.write(msg_json)
        rsp_json = self.readline()
        rsp_json = rsp_json.strip()
        rsp_json = rsp_json.decode('utf-8')
        try:
            rsp_dict = json.loads(rsp_json)
        except Exception as err:
            rsp_dict = {'ok': False, 'err': f'json parse error: {str(err)}'}
        return rsp_dict

    def enable(self):
        msg_dict = {'cmd': 'enable'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def disable(self):
        msg_dict = {'cmd': 'disable'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def is_enabled(self):
        msg_dict = {'cmd': 'is_enabled'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def set_doors(self, value):
        msg_dict = {'cmd': 'set_doors', 'doors': value}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def get_doors(self):
        msg_dict = {'cmd': 'get_doors'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def get_config(self):
        msg_dict = {'cmd': 'get_config'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def get_config_errors(self):
        msg_dict = {'cmd': 'config_errors'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict

    def get_positions(self):
        msg_dict = {'cmd': 'positions'}
        rsp_dict = self.send_and_receive(msg_dict)
        return rsp_dict





