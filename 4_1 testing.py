import serial
from abc import ABC, abstractmethod

import csv
import json
from time import sleep
from datetime import datetime


class BaseDevice(ABC):
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.delay = 0
        self.format = ['', ' ', '']
        self.connection = None
        self.connect()

        self.last_command = None


    def connect(self):
        try:
            self.connection = serial.Serial(
                self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            sleep(2)  # Wait for serial initialization
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    @abstractmethod
    def write(self, command):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def query(self, command):
        pass


class LabDevice(BaseDevice):
    def _f_command(self, command:str):
        c = '{start}' + command.strip().replace(' ', '{mid}') + '{end}'
        if c.count('{') == 3:
            return c.format(start=self.format[0],
                            mid=self.format[1],
                            end=self.format[2])
        else:
            return c.format(start=self.format[0],
                            end=self.format[2])

    def read(self):
        return self.connection.readline().decode()


    def write(self, command:str):
        if self.last_command == command:
            return
        comm = self._f_command(command)
        self.connection.write(comm.encode())
        sleep(self.delay)
        if '?' not in command:
            self.last_command = command

    def query(self, command):
        self.write(command)
        print('ждем отправку')
        return self.read()


class ZupDevice(LabDevice):
    def __init__(self, port, address=1, delay=0.015, *args, **kwargs):
        super().__init__(port, *args, **kwargs)

        self.format = [':', '', ';']
        self.delay = delay
        self.address = address
        print('load send')
        self._start_command()


    def _start_command(self):
        self.write('ADR'+str(self.address).zfill(2))


class GenesysDevice(LabDevice):
    def __init__(self, port, *args, **kwargs):
        super().__init__(port, *args, **kwargs)

        self.format = ['', ' ', '']

class N3300Device(LabDevice):
    def __init__(self, port, *args, **kwargs):
        super().__init__(port, *args, **kwargs)

        self.format = ['', ' ', '']



class TestDevice(BaseDevice):
        # Check readiness and request data

    def send(self, command):
        binary_padded = f"{command:08b}"
        self.write(binary_padded.encode())


class ExperimentLogger:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'w') as f:
            f.write("Experiment Log\n")
            f.write("Created: {}\n\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def log(self, test_number, responses):
        with open(self.filename, 'a') as f:
            f.write(f"Test #{test_number}\n")
            f.write("Responses:\n")
            for cmd, response in responses.items():
                f.write(f"   [{cmd}]: {response}\n")
            f.write("-" * 50 + "\n")



def process_experiments_4_1():
    config_dev = './configs/4_1 config_dev.csv'
    config_test = './configs/4_1 config_test.csv'
    log_file = './Report_info/a' + datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '_result.csv'

    logger = ExperimentLogger(log_file)

    data_dev, col_dev = read_file_config(config_dev)
    lab_device = [ZupDevice(port=f'COM{data_dev[0][1]}',
                            address=data_dev[0][2]),
                  ZupDevice(port=f'COM{data_dev[1][1]}',
                            address=data_dev[1][2]),
                  GenesysDevice(port=f'COM{data_dev[2][1]}'),
                  N3300Device(port=f'COM{data_dev[3][1]}')]
    test_device = TestDevice(port=f'COM{data_dev[4][1]}')

    data_test, col_test = read_file_config(config_test)
    # print(data_test)
    for id_test, com_zup1, com_zup2, genesys, n3300, cmd_dev in data_test:
        result = {}
        if type(com_zup1) == list:
            for i in com_zup1:
                if '?' in i:
                    result[i] = lab_device[0].query(i)
                else:
                    lab_device[0].write(i)
        else:
            if '?' in com_zup1:
                result.append(lab_device[0].query(com_zup1))
            else:
                lab_device[0].write(com_zup1)


        if type(com_zup2) == list:
            for i in com_zup2:
                if '?' in i:
                    result.append(lab_device[0].query(i))
                else:
                    lab_device[0].write(i)
        else:
            if '?' in com_zup2:
                result.append(lab_device[0].query(com_zup2))
            else:
                lab_device[0].write(com_zup2)


        if type(genesys) == list:
            for i in genesys:
                if '?' in i:
                    result.append(lab_device[0].query(i))
                else:
                    lab_device[0].write(i)
        else:
            if '?' in genesys:
                result.append(lab_device[0].query(genesys))
            else:
                lab_device[0].write(genesys)

        test_device.send(cmd_dev)


        if type(n3300) == list:
            for i in n3300:
                if '?' in i:
                    result.append(lab_device[0].query(i))
                else:
                    lab_device[0].write(i)
        else:
            if '?' in n3300:
                result.append(lab_device[0].query(n3300))
            else:
                lab_device[0].write(n3300)


def process_test():
    config_dev = './configs/test config_dev.csv'
    config_test = './configs/test config_test.csv'
    log_file = './Report_info/a' + datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '_result.csv'

    logger = ExperimentLogger(log_file)

    data_dev, col_dev = read_file_config(config_dev)
    lab_device = [ZupDevice(port=f'COM{data_dev[0][1]}',
                            address=data_dev[0][2])]
    # test_device = TestDevice(port=f'COM{data_dev[4][1]}')

    data_test, col_test = read_file_config(config_test)
    # print(data_test)
    for id_test, com_zup1 in data_test:
        result = {}
        if type(com_zup1) == list:
            for i in com_zup1:
                if '?' in i:
                    result[i] = lab_device[0].query(i)
                else:
                    lab_device[0].write(i)
        else:
            if '?' in com_zup1:
                result[com_zup1] = lab_device[0].query(com_zup1)
            else:
                lab_device[0].write(com_zup1)

        logger.log(id_test, result)

def create_config_dev(file_conf, data):
    with open(file_conf, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in data:
            csvwriter.writerow(row)


def read_file_config(file_name):
    data = []
    with open(file_name, "r", newline="") as f:
        reader = csv.reader(f)
        col = next(reader)  # Пропускаем заголовок
        for row in reader:
            data.append(list(map(lambda x: x.split(';') if ';' in x else x, row)))
    return data, col


if __name__ == "__main__":
    # process_test()

    a = ZupDevice(port='COM9', address=1)
    print(a.write('OUT0'))

    # a = [[1,2,3,4],
    #      [1, 2, 'awd;awe;qer 12', 4]]
    # data = [['i', '']]
    # create_config_dev()
    #
    #
    # print(read_file_config('4_1 config_dev.csv'))
    #
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # a = ZupDevice('COM1')
    # print('Подключилось')
    # a.write('ADR01')
    # a.write('OUT1')
    # print(a.query('MDL?'))
    # print(a.query('STT?'))

