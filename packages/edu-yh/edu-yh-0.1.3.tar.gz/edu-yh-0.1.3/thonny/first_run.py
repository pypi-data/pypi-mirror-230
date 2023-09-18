import os.path
import tkinter as tk
from tkinter import ttk

from thonny import is_portable, languages, ui_utils
from thonny.sqlite3_sql import data_init
import re
from tkinter import messagebox

STD_MODE_TEXT = "Standard"
RPI_MODE_TEXT = "Raspberry Pi (simple)"

UNIVERSITY = "UNIVERSITY"
PRIMARY_AND_SECONDARY = "PRIMARY_AND_SECONDARY"

PYTHON = "PYTHON"


class FirstRunWindow(tk.Tk):
    def __init__(self, configuration_manager):
        # 设置窗口的类名为 "Thonny"
        super().__init__(className="Thonny")
        ttk.Style().theme_use(ui_utils.get_default_basic_theme())

        self.title("Welcome to Thonny!" + "   [portable]" if is_portable() else "")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.ok = False

        self.conf = configuration_manager

        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=1, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.main_frame.rowconfigure(1, weight=1)

        logo_file = os.path.join(os.path.dirname(__file__), "res", "thonny.png")
        self.logo = tk.PhotoImage(file=logo_file)

        logo_label = ttk.Label(self.main_frame, image=self.logo)
        logo_label.grid(row=1, rowspan=6, column=1, sticky="nsew")

        self.padx = 50
        self.pady = 50

        self.language_variable = ui_utils.create_string_var(
            languages.BASE_LANGUAGE_NAME, self.on_change_language
        )
        self.add_combo(
            1, "Language:", self.language_variable, list(languages.LANGUAGES_DICT.values())
        )

        self.mode_variable = tk.StringVar(value=STD_MODE_TEXT)
        self.add_combo(2, "Initial settings:", self.mode_variable, [STD_MODE_TEXT, RPI_MODE_TEXT])

        tk.Label(self.main_frame, text="account").grid(row=3, column=2, sticky="sw", pady=(7, 0))
        tk.Label(self.main_frame, text="password").grid(row=4, column=2, sticky="sw", pady=(7, 0))
        self.account_entry = tk.Entry(self.main_frame)
        self.account_entry.grid(row=3, column=3, padx=(10, self.padx), sticky="sw", pady=(7, 0))

        self.password_entry = tk.Entry(self.main_frame, show="*")
        self.password_entry.grid(row=4, column=3, padx=(10, self.padx), sticky="sw", pady=(7, 0))

        self.user_type = tk.StringVar(value=PRIMARY_AND_SECONDARY)
        self.add_combo(5, "user_type:", self.user_type, [UNIVERSITY, PRIMARY_AND_SECONDARY])

        self.course_type = tk.StringVar(value=PYTHON)
        self.add_combo(6, "course_type:", self.course_type, [PYTHON])

        ok_button = ttk.Button(self.main_frame, text="Let's go!", command=self.on_ok)
        ok_button.grid(
            row=7, column=3, padx=(0, self.padx), pady=(self.pady * 0.7, self.pady), sticky="se"
        )

        self.center()

    def on_change_language(self):
        print(self.language_variable.get())

    def add_combo(self, row, label_text, variable, values):
        pady = 7
        label = ttk.Label(self.main_frame, text=label_text)
        label.grid(row=row, column=2, sticky="sw", pady=(pady, 0))
        assert isinstance(variable, tk.Variable)
        combobox = ttk.Combobox(
            self.main_frame,
            exportselection=False,
            textvariable=variable,
            state="readonly",
            height=15,
            width=20,
            values=values,
        )
        combobox.grid(row=row, column=3, padx=(10, self.padx), sticky="sw", pady=(pady, 0))

    def center(self):
        width = max(self.winfo_reqwidth(), 640)
        height = max(self.winfo_reqheight(), 300)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if screen_width > screen_height * 2:
            # probably dual monitors
            screen_width //= 2

        left = max(int(screen_width / 2 - width / 2), 0)
        top = max(int(screen_height / 2 - height / 2), 0)

        # Positions the window in the center of the page.
        self.geometry("+{}+{}".format(left, top))

    def on_ok(self):
        # 获取输入数据
        account = self.account_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()
        course_type = self.course_type.get()
        if not account:
            messagebox.showerror("登录结果", "账号不能为空")
            return
            # 校验手机号码
        pattern = r'^1[3457896]\d{9}$'
        if not re.match(pattern, account):
            messagebox.showerror(title='This is the title', message="电话号码错误", detail='请输入有效的电话号码', icon=messagebox.ERROR)
            # for child in self.fr.winfo_children():
            #     child.configure(state="normal")
            self.account_entry.config(state="normal")  # 设置账号输入框为可编辑状态
            self.password_entry.config(state="normal")  # 设置密码输入框为可编辑状态
            return

        if not password:
            messagebox.showerror("登录结果", "密码不能为空")
            return
        if len(password) < 6:
            messagebox.showerror("登录结果", "密码不能少于六位")
            return
        if self.mode_variable.get() == RPI_MODE_TEXT:
            self.conf.set_option("debugger.preferred_debugger", "faster")
            self.conf.set_option("view.ui_theme", "Raspberry Pi")
            self.conf.set_option("general.ui_mode", "simple")

        self.conf.set_option(
            "general.language", languages.get_language_code_by_name(self.language_variable.get())
        )

        self.conf.save()
        data_init(account, password, user_type, course_type)

        self.ok = True
        self.destroy()
