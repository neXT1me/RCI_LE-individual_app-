import tkinter as tk
from tkinter import ttk, scrolledtext


class LabInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторный интерфейс")
        self.root.geometry("1200x600")

        # Создание трех основных фреймов
        self.create_main_frames()

        # Заполнение первого фрейма
        self.fill_left_frame()

        # Заполнение второго фрейма
        self.fill_center_frame()

        # Заполнение третьего фрейма
        self.fill_right_frame()

    def create_main_frames(self):
        # Настройка сетки для основного окна
        self.root.grid_columnconfigure(0, weight=33)
        self.root.grid_columnconfigure(1, weight=25)
        self.root.grid_columnconfigure(2, weight=42)
        self.root.grid_rowconfigure(0, weight=1)

        # Фрейм для устройств
        self.left_frame = ttk.Frame(self.root, relief='sunken', borderwidth=2)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)

        # Фрейм для кнопок тестов
        self.center_frame = ttk.Frame(self.root, relief='sunken', borderwidth=2)
        self.center_frame.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)

        # Фрейм для консоли
        self.right_frame = ttk.Frame(self.root, relief='sunken', borderwidth=2)
        self.right_frame.grid(row=0, column=2, sticky='nsew', padx=2, pady=2)

    def fill_left_frame(self):
        # Контейнер для устройств
        devices_frame = ttk.Frame(self.left_frame)
        devices_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        # Заголовок
        ttk.Label(devices_frame, text="Состояние устройств", font='Arial 10 bold').pack(pady=5)

        # Список устройств
        self.devices = {
            'Устройство 1': tk.StringVar(value="Ошибка"),
            'Устройство 2': tk.StringVar(value="ОК"),
            'Устройство 3': tk.StringVar(value="ОК"),
            'Устройство 4': tk.StringVar(value="Ошибка")
        }

        for i, (name, status) in enumerate(self.devices.items()):
            frame = ttk.Frame(devices_frame)
            frame.pack(fill='x', pady=2)

            ttk.Label(frame, text=name, width=20).pack(side='left')
            status_label = ttk.Label(frame, textvariable=status,
                                     background='red' if status.get() == 'Ошибка' else 'green',
                                     width=10)
            status_label.pack(side='right', padx=5)

        # Кнопки внизу
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        ttk.Button(btn_frame, text="Настроить конфигурацию").pack(side='left', fill='x', expand=True)
        ttk.Button(btn_frame, text="Проверить подключение").pack(side='right', fill='x', expand=True)

    def fill_center_frame(self):
        # Контейнер с прокруткой
        canvas = tk.Canvas(self.center_frame)
        scrollbar = ttk.Scrollbar(self.center_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Создание 21 кнопки
        for i in range(21):
            btn = ttk.Button(scrollable_frame, text=f"Тест {i + 1}")
            btn.pack(fill='x', pady=1)

        # Размещение элементов
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопка автоматического тестирования
        ttk.Button(self.center_frame, text="Автоматическое тестирование").pack(
            side='bottom', fill='x', padx=2, pady=2)

    def fill_right_frame(self):
        # Консоль с прокруткой
        console = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD)
        console.pack(fill='both', expand=True, padx=5, pady=5)

        # Пример текста
        console.insert(tk.INSERT, "Готов к работе...\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = LabInterface(root)
    root.mainloop()