from tkinter import ttk

from thonny import get_workbench, ui_utils
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.tktextext import TextFrame
from thonny.ui_utils import scrollbar_style


# 定义了一个AboutDialog类，继承自ConfigurationPage类，
# 用于创建关于一个用于设置助手选项的配置页面
class AssistantConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        # 添加复选框：当程序因异常崩溃时，自动打开助手
        self.add_checkbox(
            "assistance.open_assistant_on_errors",
            tr("Open Assistant automatically when program crashes with an exception"),
            row=2,
            columnspan=2,
        )
        # 添加复选框：当有代码警告时，自动打开助手
        self.add_checkbox(
            "assistance.open_assistant_on_warnings",
            tr("Open Assistant automatically when it has warnings for your code"),
            row=3,
            columnspan=2,
        )
        # 如果已启用 Pylint，则添加复选框：执行选定的 Pylint 检查
        if get_workbench().get_option("assistance.use_pylint", "missing") != "missing":
            self.add_checkbox(
                "assistance.use_pylint", tr("Perform selected Pylint checks"), row=4, columnspan=2
            )
        # 如果已启用 MyPy，则添加复选框：执行 MyPy 检查
        if get_workbench().get_option("assistance.use_mypy", "missing") != "missing":
            self.add_checkbox("assistance.use_mypy", tr("Perform MyPy checks"), row=5, columnspan=2)

        # 添加标签：已禁用的检查（每行一个 id）
        disabled_checks_label = ttk.Label(self, text=tr("Disabled checks (one id per line)"))
        disabled_checks_label.grid(row=8, sticky="nw", pady=(10, 0), columnspan=2)

        # 创建文本框：显示已禁用的检查内容
        self.disabled_checks_box = TextFrame(
            self,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            wrap="word",
            font="TkDefaultFont",
            # cursor="arrow",
            padx=5,
            pady=5,
            height=4,
            width=30,
            borderwidth=1,
            relief="groove",
        )
        self.disabled_checks_box.grid(row=9, sticky="nsew", pady=(0, 10), columnspan=2)
        self.disabled_checks_box.text.insert(
            "1.0", "\n".join(get_workbench().get_option("assistance.disabled_checks"))
        )

        self.columnconfigure(1, weight=1)
        self.rowconfigure(9, weight=1)

    def apply(self):
        # 应用配置页面中的更改
        disabled_checks_str = (
            self.disabled_checks_box.text.get("1.0", "end")
            .replace("\r", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )
        get_workbench().set_option("assistance.disabled_checks", disabled_checks_str.splitlines())


def load_plugin():
    # 添加配置页面：助手设置页面
    get_workbench().add_configuration_page(
        "assistant", tr("Assistant（助理）"), AssistantConfigPage, 80
    )
