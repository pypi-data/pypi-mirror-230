from egse.device import DeviceInterface
from egse.decorators import dynamic_interface
from egse.command import ClientServerCommand


class Tc400Command(ClientServerCommand):
    """ Subclass to handle the checksum. Note that only kwargs are supported """


    @staticmethod
    def get_checksum(data):
        """ Checksum is the addition modulo 265 of ascii values in the dataword. """

        charsum = sum(ord(c) for c in data)
        return charsum % 256


    def get_cmd_string(self, *args, **kwargs) -> str:
        """ The TC400 commands include a checksum at the end. To avoid having to calculate this at
            the client side, it is not included in the cmd string definition in the yaml file
        """

        cmd_string = super().get_cmd_string(*args, **kwargs)
        cmd_string += f"{Tc400Command.get_checksum(cmd_string):03d}"
        cmd_string += "\r"

        return cmd_string


class Tc400Interface(DeviceInterface):

    @dynamic_interface
    def get_idn(self):
        return NotImplemented

    @dynamic_interface
    def get_last_error(self):
        return NotImplemented

    @dynamic_interface
    def get_active_speed(self):
        return NotImplemented

    @dynamic_interface
    def get_drive_power(self):
        return NotImplemented

    @dynamic_interface
    def get_motor_temperature(self):
        return NotImplemented

    @dynamic_interface
    def set_heating(self, enable):
        return NotImplemented

    @dynamic_interface
    def set_standby(self, enable):
        return NotImplemented

    @dynamic_interface
    def set_pumpingstation(self, enable):
        return NotImplemented

    @dynamic_interface
    def set_motorpump(self, enable):
        return NotImplemented

    @dynamic_interface
    def set_gasmode(self, mode):
        return NotImplemented
