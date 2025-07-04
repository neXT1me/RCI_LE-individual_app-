import serial
from time import sleep

class ZupDevice:
    _buf = None
    _conn = {}  # Словарь {port: serial.Serial}
    _instance_counts = {}  # Словарь {port: количество экземпляров}

    def __init__(self, port, address, baudrate=9600, timeout=1, delay=0.015):
        self.port = f'COM{port}'
        self.address = address
        self.baudrate = baudrate
        self.timeout = timeout
        self.delay = delay
        self.format = [':', '', ';']

        self._connection()
        self.status = self.check_link()

    def check_link(self):
            return True if self.query('MDL?') else False


    def _connection(self):
        try:
            if self.port not in ZupDevice._conn:
                ZupDevice._conn[self.port] = serial.Serial(
                    port=self.port, baudrate=self.baudrate, timeout=self.timeout
                )
                ZupDevice._instance_counts[self.port] = 0

            ZupDevice._instance_counts[self.port] += 1
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")

    def _f_command(self, command:str):
        c = '{start}' + command.strip().replace(' ', '{mid}') + '{end}'
        if c.count('{') == 3:
            return c.format(start=self.format[0],
                            mid=self.format[1],
                            end=self.format[2])
        else:
            return c.format(start=self.format[0],
                            end=self.format[2])

    def _update_buf(self):
        ZupDevice._conn[self.port].write(f':ADR{str(self.address).zfill(2)};'.encode())
        sleep(self.delay)

    def write(self, command:str):
        if ZupDevice._buf != self.address:
            self._update_buf()

        com = self._f_command(command)
        ZupDevice._conn[self.port].write(com.encode())
        sleep(self.delay)

    def read(self):
        return ZupDevice._conn[self.port].readline().decode()

    def query(self, command):
        self.write(command)
        return self.read().strip()

    def __del__(self):
        if self.port in ZupDevice._instance_counts:
            ZupDevice._instance_counts[self.port] -= 1
            if ZupDevice._instance_counts[self.port] == 0:
                self.close_connection(self.port)

    @classmethod
    def close_connection(cls, port):
        """Закрывает общее соединение."""
        if port in cls._conn:
            cls._conn[port].close()
            del cls._conn[port]
            del cls._instance_counts[port]


class GenesysDevice:
    buf = None

    def __init__(self, port, address, baudrate=9600, timeout=1, delay=0.015):
        self.port = f'COM{port}'
        self.address = address
        self.baudrate = baudrate
        self.timeout = timeout
        self.delay = delay
        self.format = ['', ' ', '']

        self.status = self.check_link()
        self.connect = self._connection()

    def check_link(self):
        return True if self.query('*IDN?') else False

    def _connection(self):
        try:
            conn = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
            return conn

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")


    def _f_command(self, command:str):
        c = '{start}' + command.strip().replace(' ', '{mid}') + '{end}'
        if c.count('{') == 3:
            return c.format(start=self.format[0],
                            mid=self.format[1],
                            end=self.format[2])
        else:
            return c.format(start=self.format[0],
                            end=self.format[2])


    def write(self, command:str):
        com = self._f_command(command)
        self.connect.write(com.encode())
        sleep(self.delay)

    def read(self):
        return self.connect.readline().decode()


    def query(self, command):
        self.write(command)
        return self.read()


class N3300:
    buf = None

    def __init__(self, port, address, baudrate=9600, timeout=1, delay=0.015):
        self.port = f'COM{port}'
        self.address = address
        self.baudrate = baudrate
        self.timeout = timeout
        self.delay = delay
        self.format = [':', '', ';']

        self.connect = self._connection()
        self.status = self.check_link()

    def check_link(self):
            return True if self.query('*IDN?') else False

    def _connection(self):
        try:
            conn = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
            return conn

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")

    def _f_command(self, command:str):
        c = '{start}' + command.strip().replace(' ', '{mid}') + '{end}'
        if c.count('{') == 3:
            return c.format(start=self.format[0],
                            mid=self.format[1],
                            end=self.format[2])
        else:
            return c.format(start=self.format[0],
                            end=self.format[2])

    def _update_buf(self):
        self.connect.write(f':ADR{str(self.address).zfill(2)};'.encode())
        sleep(self.delay)

    def write(self, command:str):
        if ZupDevice.buf != self.address:
            self._update_buf()

        com = self._f_command(command)
        self.connect.write(com.encode())
        sleep(self.delay)

    def read(self):
        return self.connect.readline().decode()


    def query(self, command):
        self.write(command)
        return self.read()


class TestDevice:
    def __init__(self, port, address=None, baudrate=9600, timeout=1, delay=0.015):
        self.port = f'COM{port}'
        self.address = address
        self.baudrate = baudrate
        self.timeout = timeout
        self.delay = delay

        self.connect = self._connection()
        self.status = self.check_link()
# ----------------------------- Выбор команды ------------------------
    def check_link(self):
            return True if self.query("Тут нужно выбрать команду") else False
# --------------------------------------------------------------------
    def _connection(self):
        try:
            conn = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
            return conn

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")

    def write(self, command:int):
        self.connect.write(command.to_bytes(1, byteorder='big'))
        sleep(self.delay)

    def read(self):
        return self.connect.read(8).decode()

    def query(self, command):
        self.write(command)
        return self.read()

def get_device(model:str):

    data = {
        'tdk-lambda zup': ZupDevice,
        'agilent n3300': N3300,
        'tdk-lambda genesys': GenesysDevice,
        'device': TestDevice
    }
    mdl = model.lower()
    for mod_dev in data.keys():
        if mod_dev in mdl:
            return data[mod_dev]

    return None
    # return data[mdl] if mdl in data.keys() else None

if __name__ == '__main__':
    # ------------------Рабочая--------------------
    # c = 21
    # a = c.to_bytes(1, byteorder='big')
    # ----------------------------
    a = ZupDevice(port=1, address=1)
    a.write('OUT 1')