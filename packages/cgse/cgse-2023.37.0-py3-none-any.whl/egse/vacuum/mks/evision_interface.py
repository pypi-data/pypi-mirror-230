from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class EvisionError(Exception):
    """ Vacscan protocol errors. """


class EvisionInterface(DeviceInterface):
    @dynamic_interface
    def control_sensor(self):
        return NotImplemented
        
    @dynamic_interface
    def release_sensor(self):
        return NotImplemented
        
    @dynamic_interface
    def filament_select(self):
        return NotImplemented
        
    @dynamic_interface
    def filament_control(self):
        return NotImplemented
        
    @dynamic_interface
    def add_bar_chart(self):
        return NotImplemented
        
    @dynamic_interface
    def add_scan(self):
        return NotImplemented
        
    @dynamic_interface
    def start_scan(self):
        return NotImplemented
        
    @dynamic_interface
    def restart_scan(self):
        return NotImplemented
    
    @dynamic_interface
    def resume_scan(self):
        return NotImplemented
    
    @dynamic_interface
    def stop_scan(self):
        return NotImplemented
    
    @dynamic_interface
    def get_mass_reading(self):
        return NotImplemented
        
    @dynamic_interface
    def get_filament_status(self):
        return NotImplemented
    
    @dynamic_interface
    def measurement_remove_all(self):
        return NotImplemented