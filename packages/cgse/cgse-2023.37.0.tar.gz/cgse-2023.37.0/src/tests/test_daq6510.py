import socket
import time

from egse.tempcontrol.keithley.daq6510 import count_number_of_channels
from egse.tempcontrol.keithley.daq6510 import get_channel_names


def test_count_number_of_channels():

    assert count_number_of_channels('(@101:106, 217, 235)') == 8
    assert count_number_of_channels('(@101:106,201:217,235:237)') == 26
    assert count_number_of_channels("(@1,2,3,4,5)") == 5
    assert count_number_of_channels("(@1, 3, 5)") == 3
    assert count_number_of_channels("(@2:7)") == 6
    assert count_number_of_channels("(@1, 2:7)") == 7


def test_get_channel_names():

    assert get_channel_names('(@101:106, 217, 235)') == [
        "101", "102", "103", "104", "105", "106", "217", "235"
    ]
    assert get_channel_names('(@101:106,201:217,235:237)') == [
        '101', '102', '103', '104', '105', '106',
        '201', '202', '203', '204', '205', '206', '207', '208', '209', '210', '211', '212', '213', '214', '215', '216', '217',
        '235', '236', '237',
    ]
    assert get_channel_names("(@1,2,3,4,5)") == ['1', '2', '3', '4', '5']
    assert get_channel_names("(@1, 3, 5)") == ['1', '3', '5']
    assert get_channel_names("(@2:7)") == ['2', '3', '4', '5', '6', '7']
    assert get_channel_names("(@1, 2:7)") == ['1', '2', '3', '4', '5', '6', '7']


# Make sure the device is turned on and connected

def request_id():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.0.20', 5025))

    rc = s.send(b'*IDN?\n')
    print(f"bytes sent: {rc=}, ", end='')

    rc = s.recv(1024)
    print(f"received: {rc=}")

    time.sleep(0)
    s.shutdown(socket.SHUT_RDWR)
    s.close()


class DAQ:
    def __init__(self):
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('192.168.0.20', 5025))

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def write(self, cmd: str):

        rc = self.socket.send(cmd.encode())

    def read(self):

        return self.socket.recv(8192)

    def trans(self, cmd: str):
        self.write(cmd)
        return self.read()


if __name__ == "__main__":
    daq = DAQ()

    daq.connect()
    daq.write('*IDN?\n')
    daq.read()
    daq.disconnect()

    daq.connect()
    daq.trans('*IDN?\n')
    daq.disconnect()

    from egse.tempcontrol.keithley.daq6510_devif import DAQ6510EthernetInterface

    daq = DAQ6510EthernetInterface('192.168.0.20', 5025)
    daq.connect()
    daq.trans('*IDN?\n')
    daq.disconnect()

    from egse.tempcontrol.keithley.daq6510 import DAQ6510Controller

    # The idea is that at the level of the controller we should not do a connect()/disconnect()
    # anymore. These should be higher level functions and the function itself should make the
    # connection to the device each time.

    daq = DAQ6510Controller('192.168.0.20', 5025)
    daq.connect()
    print(daq.info())
    daq.disconnect()
