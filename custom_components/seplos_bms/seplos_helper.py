import time
import serial
import json
import logging
_LOGGER = logging.getLogger(__name__)

import asyncio

class BMSDataCoordinator:
    _lock = asyncio.Lock()

    def __init__(self, usb_port):
        self.usb_port = usb_port
        self.data = {}
        self.last_fetch = None

    async def fetch_data(self, hass):
        async with BMSDataCoordinator._lock:  # Prevent simultaneous fetches
            if self.last_fetch is None or time.time() - self.last_fetch > 1:  # Fetch every 1 second
                self.data = await hass.async_add_executor_job(SeplosHelper.fetch_data_from_bms, self.usb_port)
                self.last_fetch = time.time()


class SeplosHelper:
    COMMAND = "~20004642E00201FD36\r"
#2000464FE00200FD23

    @staticmethod
    def twos_complement(value, bits=16):
        if (value & (1 << (bits - 1))):
            value -= 1 << bits
        return value

    @staticmethod
    def get_div(rdata, offset, divisor, precision=2, signed=False):
        N = int(rdata[offset:offset+4], 16)
        offset += 4
        if signed:
            N = SeplosHelper.twos_complement(N)
        return round(N / divisor, precision), offset

    @staticmethod
    def fetch_data_from_bms(usb_port):
        retries = 0
        max_retries = 3
        while retries < max_retries:
            data = {}
            offset = 19
            with serial.Serial(usb_port, 19200, timeout=1) as ser:
                ser.write(SeplosHelper.COMMAND.encode())
                try:
                    ser.timeout = 5
                    response = ser.read_until().decode()

                except (serial.SerialTimeoutException, serial.SerialException) as e:
                    _LOGGER.error(f"Error reading from serial port: {e}")
                    return None


            rdata = response
            if rdata[7:9] != "00":
                print(f"Error code {rdata[7:9]}. Retrying...")
                retries += 1
                time.sleep(0.1)
                continue

            # Extract NCELL and related data
            NCELL = int(rdata[17:19], 16)
            data['NoCells'] = NCELL
            highestValue = float('-inf')
            lowestValue = float('inf')
            for l in range(NCELL):
                V = int(rdata[offset:offset+4], 16)
                offset += 4
                if V > highestValue:
                    highestValue = V
                if V < lowestValue:
                    lowestValue = V
                data[f"C{l+1}"] = V

            data["HighestCell"] = highestValue
            data["LowestCell"] = lowestValue
            data["CellDifference"] = highestValue - lowestValue

            # Extract NTEMPS and related data
            NTEMPS = int(rdata[offset:offset+2], 16)
            offset += 2
            for l in range(1, NTEMPS + 1):
                T = int(rdata[offset:offset+4], 16)
                offset += 4
                T = round((T - 2731) / 10, 1)
                if l == NTEMPS - 1:
                    data["EnvTemp"] = T
                elif l == NTEMPS:
                    data["PowerTemp"] = T
                else:
                    data[f"Temp{l}"] = T


            
            # Parse remaining parameters
            data['Current'], offset = SeplosHelper.get_div(rdata, offset, 100, 2, True)
            data['Voltage'], offset = SeplosHelper.get_div(rdata, offset, 100)
            data['CapRemain'], offset = SeplosHelper.get_div(rdata, offset, 100)
            data['CapwHRemain'] = data['CapRemain'] * 48
            offset += 2
            data['Cap'], offset = SeplosHelper.get_div(rdata, offset, 100)
            data['SOC'], offset = SeplosHelper.get_div(rdata, offset, 10, 1)
            data['Capacity'], offset = SeplosHelper.get_div(rdata, offset, 100)
            data['Cycles'], offset = SeplosHelper.get_div(rdata, offset, 1, 0)
            data['SOH'], offset = SeplosHelper.get_div(rdata, offset, 10, 1)
            data['PortV'], offset = SeplosHelper.get_div(rdata, offset, 100, 2)


            return json.dumps(data)

        raise Exception("Failed to fetch data after maximum retries.")
