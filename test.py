import tkinter as tk
from tkinter import ttk

from networkx.algorithms.distance_measures import radius


class RoundedStatusLabel(tk.Canvas):
    def __init__(self, master, textvariable, radius=15, **kwargs):
        super().__init__(master, **kwargs)
        self.radius = radius
        self.textvariable = textvariable
        self.bg_color = 'white'
        self.text_id = None

        # Настройки по умолчанию
        self.config(bd=0, highlightthickness=0)
        self.width = 100  # Фиксированная ширина
        self.height = 24  # Фиксированная высота

        # Привязка к изменению переменной
        self.textvariable.trace_add('write', self._update)

        # Первоначальная отрисовка
        self._draw()

    def _draw(self):
        # Очищаем предыдущие элементы
        self.delete('all')

        # Определяем цвет фона
        status = self.textvariable.get()
        fill_color = 'red' if status == 'Ошибка' else 'green'

        # Рисуем закругленный прямоугольник
        self.create_arc(
            (0, 0, self.radius * 2, self.radius * 2),
            start=90,
            extent=90,
            fill=fill_color,
            outline=fill_color
        )
        self.create_arc(
            (self.width - self.radius * 2, 0, self.width, self.radius * 2),
            start=0,
            extent=90,
            fill=fill_color,
            outline=fill_color
        )
        self.create_arc(
            (self.width - self.radius * 2, self.height - self.radius * 2, self.width, self.height),
            start=270,
            extent=90,
            fill=fill_color,
            outline=fill_color
        )
        self.create_arc(
            (0, self.height - self.radius * 2, self.radius * 2, self.height),
            start=180,
            extent=90,
            fill=fill_color,
            outline=fill_color
        )
        self.create_rectangle(
            self.radius, 0,
            self.width - self.radius, self.height,
            fill=fill_color,
            outline=fill_color
        )
        self.create_rectangle(
            0, self.radius,
            self.width, self.height - self.radius,
            fill=fill_color,
            outline=fill_color
        )

        # Добавляем текст
        self.text_id = self.create_text(
            self.width // 2,
            self.height // 2,
            text=self.textvariable.get(),
            fill='white',
            font=('Arial', 10, 'bold')
        )

    def _update(self, *args):
        self._draw()


class Connection(tk.Frame):
    def __init__(self, parent: tk.Tk, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        # self.config(background='brown2')
        self.devices = {
            'TDK-Lambda Zup (1)': tk.StringVar(value="Ошибка"),
            'TDK-Lambda Zup (2)': tk.StringVar(value="ОК"),
            'TDK-Lambda Genesys': tk.StringVar(value="ОК"),
            'Agilent N3300': tk.StringVar(value="Ошибка")
        }

        # Основной контейнер для устройств
        devices_container = tk.Frame(self)
        devices_container.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        for name, status in self.devices.items():
            frame = tk.Frame(devices_container)
            frame.pack(fill='x', pady=5)

            tk.Label(frame, text=name, width=20, anchor='w',
                     font=('Arial', 10)).pack(side='left')

            # Используем наш новый виджет с закругленными углами
            status_label = RoundedStatusLabel(
                frame,
                textvariable=status,
                radius=12,
                width=100,
                height=24,
            )
            status_label.pack(side='right', padx=5)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self)
        btn_frame.pack(side='bottom', fill='x', padx=5, pady=10)

        tk.Button(btn_frame, text="Настроить конфигурацию",
                  relief='groove', bg='bisque', font=('Arial', 10)
                  ).pack(side='top', fill='x', pady=2)

        tk.Button(btn_frame, text="Проверить подключение",
                  relief='groove', bg='bisque', font=('Arial', 10)
                  ).pack(side='top', fill='x', pady=2)

if __name__ == '__main__':
    root = tk.Tk()
    Connection(root).pack()
    root.mainloop()