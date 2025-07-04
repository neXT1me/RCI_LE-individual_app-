import csv

from torch.onnx.symbolic_opset9 import prim_type
from datetime import datetime
from lab_devices import get_device
from os import remove


class Backend:
    def __init__(self, name_config:str, console=None):
        self.console = console
        self.config_name = name_config.strip()

        self.device_mapping = [
            'TDK-Lambda Zup (1)',
            'TDK-Lambda Zup (2)',
            'TDK-Lambda Genesys',
            'Agilent N3300',
            'Test'
        ]
        print(self._get_name_devices(self.config_name))
        self.devices = []
        self.test_device = None
        self.config = self._load_config()
        self.commands = self._load_commands()

        self.status_flag = False

        self.name_file_report = ('./Report_info/' + 'Report_'
                                 + datetime.now().isoformat()[:19].replace(':', '_')
                                 + '.txt')
        self.f_report = open(self.name_file_report, 'a')
        self.flag_empty_file_report = True

    def _get_name_devices(self, config_name):
        return [conf[0] for conf in self._load_csv(config_name + ' config_dev.csv')]

    def _init_devices(self):
        """
        Инициализация устройств на основе конфигурации
        """
        self.print_console('-Проверка подключения устройств:')

        self.devices.clear()

        status_devices = []


        for mdl_id in range(len(self.device_mapping)):
            try:
                self.devices.append(get_device(self.device_mapping[mdl_id])(port=self.config[mdl_id+1][1],
                                                                            address=self.config[mdl_id+1][2]))
                status_devices.append(self.devices[-1].status)

                self.print_console(f'\t{mdl_id+1}) {self.device_mapping[mdl_id]} --- '
                                   f'{'Подключено' if status_devices[-1] else 'Нет ответа от устройства'}')
            except:
                status_devices.append(False)
                self.print_console(f'\t{mdl_id + 1}) {self.device_mapping[mdl_id]} --- '
                                   f'Данного COM порта не существует')

        self.status_flag = all(status_devices)
        return status_devices


    def _save_config(self):
        with open('configs/4_1 config_dev.csv', 'w', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(self.config, )

    def _load_csv(self, file):
        result = []
        with open(file, 'r') as f:
            for i in csv.reader(f):
                if i:
                    result.append(i)
        return result

    def _load_config(self):
        result = []
        with open('configs/4_1 config_dev.csv', 'r') as f:
            for i in csv.reader(f):
                result.append(i)
        return result

    def _load_commands(self):
        result = []
        with open('configs/4_1 config_test.csv', 'r') as f:
            for i in csv.reader(f):
                result.append([j.split(';') if ';' in j else [j] for j in i])
        return result

    @staticmethod
    def _check_data(data:str):
        for com_adr in data:
            for value in com_adr:
                if not (value.isdigit() and (0 < int(value) <= 32)):
                    return False
        return True

    def _create_report(self, id_test, results:dict[str, dict]):
        text = f'{'-'*10} Test #{id_test} {'-'*10}\n'
        if results:
            if self.flag_empty_file_report:
               self.flag_empty_file_report = False
            for dev, result_params in results.items():
                text += f'{dev}:\n'
                for cmd, result in result_params.items():
                    text += f'\t{cmd}: {result}\n'
        else:
            text += 'Нет данных для отображения'


        self.print_console(text)
        self.f_report.write(text)





    def update_config(self, data):
        if not self._check_data(data):
            return False

        for row, (com, adr) in enumerate(data, start=1):
            self.config[row][1] = com
            self.config[row][2] = adr

        self._save_config()
        self.print_console('- Конфигурация устройств изменена')
        return True

    def check_connection(self):
        return self._init_devices()

    def value_commands(self):
        return len(self.commands)-1

    def print_console(self, text):
        self.console.insert(text)

    def command_execution(self, index_command:int):
        print(index_command)
        print(*self.commands, sep='\n')
        if not self.status_flag:
            self.print_console('####### Ошибка: некоторые устройства не подключены\n'
                                      '####### Проверьте подключение всех устройств')
            return False

        results = {}
        for dev, list_cmd in zip(range(len(self.devices)), self.commands[index_command][1:]):
            results[self.device_mapping[dev]] = {}

            for cmd in list_cmd:
                if '?' in cmd:
                    answer = self.devices[dev].query(cmd)
                    results[self.device_mapping[dev]][cmd] = answer
                else:
                    self.devices[dev].write(cmd)

        for key in list(results):
            if not results[key]:
                del results[key]

        self._create_report(index_command, results)
        return True

    def __del__(self):
        self.devices.clear()
        self.f_report.close()
        if self.flag_empty_file_report:
            remove(self.name_file_report)





if __name__ == '__main__':
    a = Backend()
    print(a._init_devices())