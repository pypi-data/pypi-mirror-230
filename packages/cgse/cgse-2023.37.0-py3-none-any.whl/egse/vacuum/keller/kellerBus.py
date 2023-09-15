from struct import unpack, pack
from serial import Serial

class kellerBusBadAddress(Exception):
    def __init__(self):
        super().__init__("Invalid KellerBus address")

class kellerBusException1(Exception):
    def __init__(self):
        super().__init__("Illegal, non-implemented function")

class kellerBusBadCrcException(Exception):
    def __init__(self):
        super().__init__("CRC is incorrect")

class kellerBusException2(Exception):
    def __init__(self):
        super().__init__("Illegal data address")
 
class kellerBusException3(Exception):
    def __init__(self):
        super().__init__("Illegal data value")        

class kellerBusException32(Exception):
    def __init__(self):
        super().__init__("Initialization required")
        
class kellerBusBadException(Exception):
    def __init__(self):
        super().__init__("Incorrect data received")

class kellerBusNotReadable(Exception):
    def __init__(self):
        super().__init__("No data received as response")
    
class kellerBusRxException(Exception):
    def __init__(self):
        super().__init__("Received bad data")

class kellerBus(Serial):
    def __init__(self, port, baudrate, timeout=0.2):
        super().__init__(port=port, baudrate=baudrate, timeout=timeout)

    def calculateCrc16(self, data: bytes):
        crc = 0xFFFF
        
        for byte in data:
            crc = int(crc ^ byte)
            for bit in range(8):
                b = True if crc % 2 ==1 else False
                crc = int(crc / 2)
                crc = int(crc ^ 0xA001) if b else crc
                
        high, low = crc >> 8, crc & 0x00FF
        return high, low


    def transferData(self, txBuf, nRead):
        self.reset_input_buffer()
        self.reset_output_buffer()

        txHigh, txLow = self.calculateCrc16(bytes(txBuf))
        
        txBuf.append(txHigh)
        txBuf.append(txLow)
#        print(txBuf)
        self.write(txBuf)
        
        rxBuf = self.read(nRead)
        
#        print(rxBuf)

        if len(rxBuf) == 0:
            raise kellerBusNotReadable()
        
        rxHigh, rxLow = self.calculateCrc16(bytes(rxBuf[:-2]))
        
        if (rxBuf[-2] != rxHigh) or (rxBuf[-1] != rxLow):
            raise kellerBusBadCrcException()
        
        if txBuf[0] != rxBuf[0]:
             raise kellerBusBadAddress()
        
        if txBuf[1] == rxBuf[1]: 
            return rxBuf
        
        if rxBuf[2] == 1:
            raise kellerBusException1()
        elif rxBuf[2] == 2:
            raise kellerBusException2()
        elif rxBuf[2] == 3:
            raise kellerBusException3()
        elif rxBuf[2] == 32:
            raise kellerBusException32()
        else:
            raise kellerBusBadException()
            
        raise kellerBusRxException()


    def F48(self, address):
        ''' Initialize Keller Bus device
        
        : param address = int Device address
        '''
        code = 48
        nRead = 10
        txBuf = [address, code]
        try:
            rxBuf = self.transferData(txBuf, nRead)

            data = {
            "deviceClass"  :rxBuf[2],
            "deviceGroup"  :rxBuf[3],
            "deviceYear"   : rxBuf[4],
            "deviceWeek"   :rxBuf[5],
            "deviceBuffer" :rxBuf[6],
            "deviceState"  : rxBuf[7]
            }
            
            return data
            
        except Exception as exc:
            raise exc


    def F30(self, address, coef):
        code = 30
        nRead = 8
        txBuf = [address, code, coef]
        
        try:
            rxBuf = self.transferData(txBuf, nRead)
            
            return unpack('f', rxBuf[2:6])[0]

        except Exception as exc:
            raise exc

   
    def F31(self, address, coef, value):
        code = 31
        nRead = 5
        value = pack('f', value)
        txBuf = [address, code, coef]
        txBuf += value
        try:
            rxBuf = self.transferData(txBuf, nRead)
            return True
        except Exception as exc:
            raise exc

    def F32(self, address, num):
        code =  32
        nRead = 5
        txBuf = [address, code, num]
        try:
            rxBuf = self.transferData(txBuf, nRead)
            return rxBuf[3]
        except Exception as exc:
            raise exc
        
        
    def F66(self, address, new_address):
        code = 66
        nRead = 5
        txBuf = [address, code, new_address]
        try:
            rxBuf = self.transferData(txBuf, nRead)
            return rxBuf[3]
        except Exception as exc:
            raise exc


    def F69(self, address):
        code = 69
        nRead = 8
        txBuf = [address, code]
        try:
            rxBuf = self.transferData(txBuf, nRead)
            return 256*65536*rxBuf[3]*65536*rxBuf[4]*256*rxBuf[5]*rxBuf[6]
        except Exception as exc:
            raise exc


    def F73(self, address, channel):
        code = 73
        nRead = 9
        txBuf = [address, code, channel]
        try:
            rxBuf = self.transferData(txBuf, nRead)
            
            value = unpack('!f', rxBuf[2:6])

            return value[0], rxBuf[6]
        except Exception as exc:
            raise exc


    def F95(self, address, command):
        code = 95
        nRead = 9
        txBuf = [address, code, command]
        try:
            self.transferData(txBuf, nRead)
            return True
        except Exception as exc:
            raise exc

   
    def F95_val(self, address, command, value):
        code = 95
        nRead = 9
        txBuf = [address, code, command, value]
        try:
            self.transferData(txBuf, nRead)
            return True
        except Exception as exc:
            raise exc


    def F100(self, address, index):
        code = 100
        nRead = 9
        txBuf = [address, code, index]
        try:
            rxBuf = self.transferData(txBuf, nRead)         
            
            data = {
                'PARA0': f"{rxBuf[2]:08b}",
                'PARA1': f"{rxBuf[3]:08b}",
                'PARA2': f"{rxBuf[4]:08b}",
                'PARA3': f"{rxBuf[5]:08b}",
                'PARA4': f"{rxBuf[6]:08b}"
                }
            
            return data
        except Exception as exc:
            raise exc

def main():
    leo3 = []

    leo3 = kellerBus('/dev/ttyUSB0', 9600, 2)

    for idx in [1, 2, 3, 4, 5, 6]:
        print(f"Keller LEO3 address: {idx}")
        print(leo3.F48(idx))
        print(leo3.F100(idx, 2))
    while 1:
        for idx in [1, 2, 3, 4, 5, 6]:
            print(f"Address : {idx}, Pressure: {leo3.F73(idx, 1)}, Temperature: {leo3.F73(idx, 4)}")

    
if __name__ == "__main__":
    main()
