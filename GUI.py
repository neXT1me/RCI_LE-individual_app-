import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext, ttk
import serial
import serial.tools.list_ports
import time
import csv
import os
from Core import Backend

class Commands(tk.Frame):
    '''
    Данный класс служит Frame-ом для отображения
    '''
    def __init__(self, parent, backend:Backend, *args, **kw):
        tk.Frame.__init__(self, parent, *args,  **kw)
        self.backend = backend
        self.parent = parent

        self.vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.interior = interior = tk.Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        lis = list(range(self.backend.value_commands()))
        for i, x in enumerate(lis, start=1):
            print(i)
            btn = tk.Button(self.interior, height=1,
                            width=20, relief=tk.FLAT,
                            bg="gray99", font="Dosis",
                            text='Команда ' + str(lis[i-1]+1),
                            command=lambda num=i: self._start_command(num)
                            )
            btn.pack(padx=10, pady=5, side=tk.TOP)

        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.config(width=interior.winfo_reqwidth())

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())

        self.interior.bind('<Configure>', _configure_interior)
        self.canvas.bind('<Configure>', _configure_canvas)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x')

        self.auto_btn = tk.Button(bottom_frame, height=2, width=20,
                                  bg="gray99", relief=tk.FLAT,
                                  font="Dosis",text="Автоматическое \nтестирование",
                                  command=self._start_all_commands)
        self.auto_btn.pack(fill='x', padx=5, pady=5)

    def _start_command(self, index_command):
        return self.backend.command_execution(index_command)

    def _start_all_commands(self):
        for i in list(range(1, self.backend.value_commands())):
            if not self._start_command(i):
                break


# Класс с frame для подключения устройств
class Configuration(tk.Toplevel):
    '''
    Данный класс служит Frame-ом для отображения и изменения конфигураций
    устройств для подключения по COM портам
    '''
    def __init__(self, parent, backend:Backend, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.backend = backend

        self.geometry('400x200')
        self.resizable(False, False)
        self.title("Настройка конфигурации")

        # Конфигурация сетки
        self.grid_columnconfigure(0, weight=1, uniform='col')
        self.grid_columnconfigure(1, weight=1, uniform='col')
        self.grid_columnconfigure(2, weight=1, uniform='col')

        # Заголовки
        headers = ['Модель', 'COM порт', 'Адрес устройства']
        for col, text in enumerate(headers):
            tk.Label(self, text=text, font=('Arial', 10, 'bold'),
                     borderwidth=1, relief='groove', padx=5, pady=5
                     ).grid(row=0, column=col, sticky='nsew', padx=1, pady=1)

        # Список устройств
        self.devices = ['TDK-Lambda Zup (1)', 'TDK-Lambda Zup (2)',
                   'TDK-Lambda Genesys', 'Agilent N3300', 'Test']

        self.com_list_widg = []
        self.adr_list_widg = []

        # Создание строк с настройками
        self.entries = []
        for row, device in enumerate(self.devices, start=1):
            # Метка с названием устройства
            tk.Label(self, text=device, anchor='w',
                     font=('Arial', 9), padx=5
                     ).grid(row=row, column=0, sticky='nsew')

            # Поле для COM порта
            com_entry = ttk.Entry(self, width=15, font=('Arial', 10))
            self.com_list_widg.append(com_entry)
            com_entry.insert(0, self.backend.config[row][1])
            com_entry.grid(row=row, column=1, sticky='nsew', padx=2, pady=2)

            # Поле для адреса устройства
            addr_entry = ttk.Entry(self, width=15, font=('Arial', 10))
            self.adr_list_widg.append(addr_entry)
            addr_entry.insert(0, self.backend.config[row][2])
            addr_entry.grid(row=row, column=2, sticky='nsew', padx=2, pady=2)

            self.entries.append((com_entry, addr_entry))

        # Фрейм для кнопок
        button_frame = ttk.Frame(self)
        button_frame.grid(row=len(self.devices) + 1, column=0, columnspan=3,
                          sticky='se', pady=10, padx=10)

        # Кнопки
        ttk.Button(button_frame, text="Отмена",).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Сохранить", command=self.save_configurate).pack(side='right')

        # Выравнивание строк
        for i in range(1, len(self.devices) + 1):
            self.grid_rowconfigure(i, weight=1, uniform='row')

    def save_configurate(self):
        data = list(zip([i.get() for i in self.com_list_widg],
                    [i.get() for i in self.adr_list_widg]))
        result = self.backend.update_config(data=data)

        if not result:
            text = 'Вводные данные должны содержать только целые числа от 1 до 32'
            messagebox.showerror('Ошибка данных', text)


class Connection(tk.Frame):
    '''
    Данный класс служит Frame-ом для отображения подключенных устройств,
    Что расположены в файлах конфигурации
    '''
    def __init__(self, parent:tk.Tk, backend:Backend, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.backend = backend
        self.devices = {
            'TDK-Lambda Zup (1)': [tk.StringVar(value="Ошибка")],
            'TDK-Lambda Zup (2)': [tk.StringVar(value="Ошибка")],
            'TDK-Lambda Genesys': [tk.StringVar(value="Ошибка")],
            'Agilent N3300': [tk.StringVar(value="Ошибка")],
            'Device': [tk.StringVar(value="Ошибка")]
        }
        for name, status in self.devices.items():
            frame = tk.Frame(self)
            frame.pack(fill='x', pady=2)

            tk.Label(frame, text=name,
                     width=20,
                     anchor='w',
                     font=('Arial', 10)).pack(side='left')
            status_label = tk.Label(frame,
                                    textvariable=status[0],
                                     background='red' if status[0].get() == 'Ошибка' else 'green',
                                     width=10)

            status_label.pack(side='right', padx=5)
            status.append(status_label)

        btn_frame = tk.Frame(self)
        btn_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        tk.Button(btn_frame, height=1, width=20, relief=tk.FLAT,
                        bg="gray99",
                        font="Dosis", text="Настроить конфигурацию",
                  command=lambda:self._open_configuration(self.backend)).pack(side='top', fill='x', pady=2)
        tk.Button(btn_frame, height=1, width=20, relief=tk.FLAT,
                        bg="gray99",
                        font="Dosis", text="Проверить подключение",
                        command=self._check_connections).pack(side='top', fill='x', pady=2)

    def _open_configuration(self, backend):
        self.configuration = Configuration(self.parent, backend)
        self.configuration.grab_set()
        self.configuration.focus_set()
        self.configuration.wait_window()

    def _update_status(self, name_dev, status:bool) -> None:
        self.devices[name_dev][0].set("ОК" if status else "Ошибка")
        self.devices[name_dev][1].config(background='green' if status else 'red')

    def _check_connections(self):
        result_flags = self.backend.check_connection()
        for dev, status in zip(self.devices, result_flags):
            self._update_status(dev, status)



# Класс фрейма с консолью
class Console(tk.Frame):
    def __init__(self, parent:tk.Tk, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.console_font = ('DejaVu Sans Mono', 10)
        self.console = scrolledtext.ScrolledText(self, wrap=tk.WORD,
            font=self.console_font,
            undo=True,
            insertbackground='white',
            state="disabled"
        )
        self.console.pack(fill='both', expand=True, padx=5, pady=5)

        self.console.insert(tk.INSERT, 'Готов к работе ...\n')

    def insert(self, text:str) -> None:
        self.console.config(state="normal")
        self.console.insert('end', text + '\n')
        self.console.config(state="disabled")


class MainApplication(tk.Frame):
    def __init__(self, parent: tk.Tk, backend:Backend, config_name:str, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.backend = backend

        # Настройка пропорций колонок
        self.parent.grid_columnconfigure(0, weight=33)
        self.parent.grid_columnconfigure(1, weight=25)
        self.parent.grid_columnconfigure(2, weight=42)
        self.parent.grid_rowconfigure(0, weight=1)

        # Создание и размещение фреймов


        self.conn = Connection(self.parent, self.backend)
        self.cmd = Commands(self.parent, self.backend)

        self.consl = Console(self.parent)
        self.backend.console = self.consl


        self.conn.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        self.cmd.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
        self.consl.grid(row=0, column=2, sticky='nsew', padx=2, pady=2)


def main(name_config='4_1'):
    config_name = './configs/' + name_config
    root = tk.Tk()
    MainApplication(root, Backend(config_name), config_name)
    root.mainloop()


if __name__ == "__main__":
    main()
