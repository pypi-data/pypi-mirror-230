from egse.decorators import dynamic_interface
from egse.control import Response, Success


class FdirRemoteInterface:
    """ Descriptions of the interface can be found in the corresponding yaml file. """

    @dynamic_interface
    def kill_process(self, pid: int) -> Response:
        raise NotImplementedError

    @dynamic_interface
    def generate_popup(self, code: int, actions, success) -> Response:
        raise NotImplementedError
