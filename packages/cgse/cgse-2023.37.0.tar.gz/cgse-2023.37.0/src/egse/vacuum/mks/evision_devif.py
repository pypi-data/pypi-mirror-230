import logging
import time
import asyncio

from threading import Thread

from egse.socketdevice                  import SocketDevice
from egse.command                       import Command
from egse.settings                      import Settings
from egse.vacuum.mks.evision_interface  import EvisionInterface

logger = logging.getLogger(__name__)

class EvisionException(Exception):
    pass

class EvisionDriver(SocketDevice, EvisionInterface):
    def __init__(self, host=None, port=None):
        self._host = '192.168.1.70' if host == None else host
        self._port = 10014          if port == None else port
        
        super().__init__(hostname=self._host, port=self._port, timeout=2)
        self.connect()
        
        self.filament_num = 0
        
        self.filament = {
            'SummaryState' : None,
            'ActiveFilament' : None,
            'ExternalTripEnable' : None,
            'ExternalTripMode' : None,
            'EmissionTripEnable': None,
            'MaxOnTime' : None,
            'OnTimeRemaining' : None,
            'Trip' : None,
            'Drive' : None,
            'EmissionTripState' : None,
            'ExternalTripState' : None,
            'RVCTripState' : None,
            'GaugeTripState' : None
        }
        
        self.status = {
            'SerialNumber' : None,
            'Name' : None,
            'State' : None,
            'UserApplication' : None,
            'UserAddress' : None,
            'ProductID' : None,
            'DetectorTType' : None,
            'TotalPressureGauge' : None,
            'FilamentType' : None,
            'SensorType' : None,
            'MaxMass' : None,
            'ActiveFilament' : None
        }
        
        self.current_scan = {
            'Name' : None,
            'StartMass' : None,
            'EndMass' : None,
            'FilterMode' : None,
            'Accuracy' : None,
            'EGainIndex' : None,
            'SourceIndex' : None,
            'DetectorIndex' : None,
            'Running': False
        }
        
        self.mass_reading = [0] * 200
        self.zero_reading = None
        
        self.thread = Thread(target=self.reader_thread, daemon=True)
        self.thread.start()
                
    def reader_thread(self):
        while True:
            try:
                responses = self.wait_for_response().split(b'\r\n\r\r')
            except:
                # logger.info("No response")
                pass
            else:
                try:
                    for response in responses:
                        if b'Control' in response:
                            if b'OK' in response:
                                pass
                            else:
                                logger.warning("Could not control sensor")  
                                
                        if b'Release' in response:
                            if b'OK' in response:
                                pass
                            else:
                                logger.warning("Could not release sensor")
                                
                        elif b'FilamentSelect' in response:
                            response = response.decode()
                            response = response.split('\r\n')
                            
                            self.filament_num                   = response[1].split()[-1]
                            
                        elif b'FilamentControl' in response:
                            response = response.decode()
                            response = response.split('\r\n')
                        
                        elif b'FilamentStatus' in response:
                            response = response.decode()
                            response = response.split('\r\n')
                            
                            self.filament_num                   = response[0].split()[1]
                            self.filament['SummaryState']       = response[0].split()[-1]
                            self.filament['Trip']               = response[1].split()[-1]
                            self.filament['Drive']              = response[2].split()[-1]
                            self.filament['EmissionTripEnable'] = response[3].split()[-1]
                            self.filament['ExternalTripState']  = response[4].split()[-1]
                            self.filament['RVCTripState']       = response[5].split()[-1]
                            self.filament['GaugeTripState']     = response[6].split()[-1]
                        
                        elif b'FilamentTimeRemaining' in response:
                            response.decode()
                            print(f"Filament time remaining: {response}")
                            self.filament['OnTimeRemaining'] = response[-1]
                        
                        elif b'FilamentInfo' in response:
                            response = response.decode()
                            response = response.split('\r\n')

                            self.filament['SummaryState']       = response[1].split()[-1]
                            self.filament['ActiveFilament']     = response[2].split()[-1]
                            self.filament['ExternalTripEnable'] = response[3].split()[-1]
                            self.filament['ExternalTripMode']   = response[4].split()[-1]
                            self.filament['EmissionTripEnable'] = response[5].split()[-1]
                            self.filament['MaxOnTime']          = response[6].split()[-1]
                            self.filament['OnTimeRemaining']    = response[7].split()[-1]
                            self.filament['Trip']               = response[8].split()[-1]
                            self.filament['Drive']              = response[9].split()[-1]
                            self.filament['EmissionTripState']  = response[10].split()[-1]
                            self.filament['ExternalTripState']  = response[11].split()[-1]
                            self.filament['RVCTripState']       = response[12].split()[-1]
                            self.filament['GaugeTripState']     = response[13].split()[-1]
                            
                        elif b'Info  OK' in response:
                            response = response.decode()
                            response = response.split('\r\n') 

                            self.status = {
                                'SerialNumber'          : response[1].split()[-1],
                                'Name'                  : response[2].split()[-1],
                                'State'                 : response[3].split()[-1],
                                'UserApplication'       : response[4].split()[-1],
                                'UserAddress'           : response[6].split()[-1],
                                'ProductID'             : ' '.join(response[7].split()[2:]),
                                'DetectorType'          : ''.join(response[9].split()[2:]),
                                'TotalPressureGauge'    : ' '.join(response[12].split()[2:]),
                                'FilamentType'          : response[13].split()[-1],
                                'SensorType'            : ' '.join(response[15].split()[2:]),
                                'MaxMass'               : response[24].split()[-1],
                                'ActiveFilament'        : response[25].split()[-1]
                            }
                            
                        elif b'AddBarchart' in response:
                            response = response.decode()
                            response = response.split('\r\n')
                            
                            self.current_scan = {
                                'Name'          : response[1].split()[-1],
                                'StartMass'     : response[2].split()[-1],
                                'EndMass'       : response[3].split()[-1],
                                'FilterMode'    : response[4].split()[-1],
                                'Accuracy'      : response[5].split()[-1],
                                'EGainIndex'    : response[6].split()[-1],
                                'SourceIndex'   : response[7].split()[-1],
                                'DetectorIndex' : response[8].split()[-1],
                                'Running'       : False
                            }

                        elif b'StartingScan' in response:
                            self.current_scan['Running'] = True
        
                        elif b'ScanAdd' in response:
                            if b'OK' in response:
                                pass
                            else:
                                logger.warning("Could not add scan")
                        
                        elif b'ScanStart' in response:
                            if b'OK' in response:
                                pass
                            else:
                                logger.warning("Could not start scan")
                        
                        elif b'StartingMeasurement' in response:
                            response = response.decode()
                            self.current_scan['Name'] = response.split()[-1]
                            
                        elif b'MassReading' in response:
                            response = response.decode()
                            
                            mass_num = response.split()[1]
                            mass     = response.split()[-1]
                            
                            self.mass_reading[int(mass_num)] = float(mass)
                        
                        elif b'ZeroReading' in response:
                            response = response.decode()
                            
                            mass = response.split()[-1]
                            
                            self.zero_reading = mass
                            self.mass_reading = [0] * 200
                except Exception as ex:
                    logger.warning("Received invalid response from RGA")

    
    def control_sensor(self):
        self.send_command('Control "Common-EGSE" "1.0"\r\n')
    
    def release_sensor(self):
        self.send_command("Release\r\n")
    
    def filament_status(self):
        self.send_command("FilamentInfo\r\n")    
    
    def rga_status(self):
        self.send_command("Info\r\n")
    
    def filament_select(self, num):
        self.send_command(f"FilamentSelect {num}\r\n")

    def filament_control(self, state):
        control = 'On' if state else 'Off'
        self.send_command(f"FilamentControl {control}\r\n")
        
    def add_bar_chart(self, name, startMass=1, endMass=100, filterMode='PeakCenter', accuracy=5, eGainIndex=0, sourceIndex=0, detectorIndex=0):
        filterMode = 'PeakCenter' if filterMode == 'Peak center' else filterMode
        self.send_command(f"AddBarchart {name} {startMass} {endMass} {filterMode} {accuracy} {eGainIndex} {sourceIndex} {detectorIndex}\r\n")
    
    def add_single_peak(self, name, mass=4, accuracy=5, eGainIndex=0, sourceIndex=0, detectorIndex=0):
        self.send_command(f"AddSinglePeak {name} {mass} {accuracy} {eGainIndex} {sourceIndex} {detectorIndex}\r\n")
    
    def add_peak_jump(self, name, filterMode='PeakCenter', accuracy=5, eGainIndex=0, sourceIndex=0, detectorIndex=0):
        self.send_command(f"AddPeakJump {name} {filterMode} {accuracy} {eGainIndex} {sourceIndex} {detectorIndex}\r\n")
    
    def add_analog(self, name, startMass=1, endMass=50, pointsPerPeak=32, accuracy=5, eGainIndex=0, sourceIndex=0, detectorIndex=0):
        self.send_command(f'AddAnalog {name} {startMass} {endMass} {pointsPerPeak} {accuracy} {eGainIndex} {sourceIndex} {detectorIndex}\r\n')
    
    def measurement_add_mass(self, mass):
        self.send_command(f'MeasurementAddMass {mass}\r\n')
    
    def measurement_remove_mass(self, mass):
        self.send_command(f"MeasurementRemoveMass {mass}\r\n")
    
    def measurement_remove_all(self):
        self.send_command(f"MeasurementRemoveAll\r\n")
    
    def measurement_remove(self, name):
        self.send_command(f"MeasurementRemove {name}\r\n")
    
    def add_scan(self, name):
        self.send_command(f'ScanAdd {name}\r\n')
    
    def start_scan(self, num):
        self.send_command(f'ScanStart {num}\r\n')
        
    def stop_scan(self):
        self.send_command(f'ScanStop\r\n')
        
    def resume_scan(self, num):
        self.send_command(f'ScanResume {num}\r\n')
        
    def restart_scan(self):
        self.send_command(f'ScanRestart\r\n')
        
    def get_mass_reading(self):
        return self.mass_reading
    
    def get_filament_status(self):
        return self.filament
    
    def get_rga_status(self):
        return self.status
    
    def get_scan_status(self):
        return self.current_scan
    
def main():
    dev = EvisionDriver()
    
    dev.control_sensor()
    
    dev.filament_select(1)
    dev.filament_control(True)
    
    while dev.filament['SummaryState'] == 'On':
        time.sleep(1)
    
    dev.add_bar_chart(name='Bar', startMass=1, endMass=10, filterMode='PeakCenter', accuracy=5, eGainIndex=0, sourceIndex=0, detectorIndex=0)
    dev.add_scan(name='bar')
    dev.start_scan(1)
    
    time.sleep(5)
    
    print(dev.mass_reading)
    print(dev.zero_reading)
    # dev.filament_status()
    
    
    # time.sleep(2)
    
    # print(dev.filament_num)
    # print(dev.filament)
    
if __name__ == "__main__":
    main()