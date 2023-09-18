import tkinter as tk
from datetime import datetime
from tkinter import ttk

from tkcalendar import DateEntry


class DateTimePicker:
    def __init__(self, parent, show_text):
        self.parent = parent
        self.selected_datetime = None

        # 创建一个标签显示 "开始时间"
        label_start_time = ttk.Label(self.parent, text=show_text)
        label_start_time.pack()

        # 创建日历组件
        self.calendar = DateEntry(
            self.parent, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        self.calendar.pack(pady=10)

        # 创建时间选择组件
        self.time_frame = ttk.Frame(self.parent)

        # 创建小时选择下拉菜单
        hour_label = ttk.Label(self.time_frame, text="小时：")
        hour_label.grid(row=0, column=0, padx=5, pady=5)
        self.hour_combo = ttk.Combobox(self.time_frame, values=[str(i).zfill(2) for i in range(24)])
        self.hour_combo.current(0)
        self.hour_combo.grid(row=0, column=1, padx=5, pady=5)

        # 创建分钟选择下拉菜单
        minute_label = ttk.Label(self.time_frame, text="分钟：")
        minute_label.grid(row=1, column=0, padx=5, pady=5)
        self.minute_combo = ttk.Combobox(
            self.time_frame, values=[str(i).zfill(2) for i in range(60)]
        )
        self.minute_combo.current(0)
        self.minute_combo.grid(row=1, column=1, padx=5, pady=5)

        self.time_frame.pack()

        # # 创建按钮用于获取选定的日期和时间
        # get_time_button = ttk.Button(self.parent, text="获取时间", command=self.get_selected_datetime)
        # get_time_button.pack(pady=10)

    def get_selected_datetime(self):
        date = self.calendar.get_date()
        date_str = date.strftime("%m/%d/%y")  # 将日期对象转换为字符串
        time = f"{self.hour_combo.get()}:{self.minute_combo.get()}:00"

        # 将日期时间转换为指定格式
        self.selected_datetime = (
            datetime.strptime(date_str, "%m/%d/%y").strftime("%Y-%m-%d") + " " + time
        )
        return self.selected_datetime
