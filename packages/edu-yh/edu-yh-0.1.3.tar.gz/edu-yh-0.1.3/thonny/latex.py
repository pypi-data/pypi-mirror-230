from thonny import get_workbench, tktextext, ui_utils
from thonny.languages import tr
from thonny.ui_utils import scrollbar_style
import subprocess
import shutil
import uuid
from tkinter import filedialog
from thonny.misc_utils import running_on_mac_os, running_on_linux
import tkinter as tk

preview_content = ""

class LatextView(tktextext.TextFrame):
    def __init__(self, master):
        tktextext.TextFrame.__init__(
            self,
            master,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            read_only=True,
            font="TkDefaultFont",
            padx=10,
            pady=0,
            insertwidth=0,
        )

        self.preview_content = preview_content



def preview_latex(content):
    name = str(uuid.uuid4())

    # 将 LaTeX 内容保存到 .tex 文件中
    with open(name + ".tex", "w", encoding="utf-8") as tex_file:
        tex_file.write(content)

    try:
        # 使用 pdflatex 编译 LaTeX 文件并指定输出目录
        if running_on_linux() or running_on_mac_os():
            subprocess.run(["pdflatex", name + ".tex"])
        else:
            subprocess.run(["pdflatex", name + ".tex"], shell=True)  # Windows

        print("LaTeX 编译成功")
        # 读取生成的 PDF 文件内容
        with open(name + ".pdf", "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # 显示 LaTeX 预览
        global preview_content
        preview_content = pdf_content
        get_workbench().show_view("LatextView", set_focus=False)
    except subprocess.CalledProcessError:
        print("LaTeX 编译失败")
    finally:
        # 清理生成的临时文件
        if running_on_linux() or running_on_mac_os():
            subprocess.run(["rm", name + ".tex", name + ".aux", name + ".log"])  # Linux/MacOS
        else:
            subprocess.run(["del", name + ".tex", name + ".aux", name + ".log"], shell=True)  # Windows


def create_latex(content):
    output_folder = filedialog.askdirectory(title="选择输出文件夹")

    name = str(uuid.uuid4())

    # 将 LaTeX 内容保存到 .tex 文件中
    with open(name + ".tex", "w", encoding="utf-8") as tex_file:
        tex_file.write(content)

    try:
        # 使用 pdflatex 编译 LaTeX 文件并指定输出目录
        if running_on_linux() or running_on_mac_os():
            subprocess.run(["pdflatex", name + ".tex"])
        else:
            subprocess.run(["pdflatex", name + ".tex"], shell=True)  # Windows

        # 移动生成的 PDF 文件到指定位置
        shutil.move(name + ".pdf", output_folder)

        print("LaTeX 编译成功")
    except subprocess.CalledProcessError:
        print("LaTeX 编译失败")
    finally:
        # 清理生成的临时文件
        if running_on_linux() or running_on_mac_os():
            subprocess.run(["rm", name + ".tex", name + ".aux", name + ".log", name + ".pytxcode"])  # Linux/MacOS
        else:
            subprocess.run(["del", name + ".tex", name + ".aux", name + ".log", name + ".pytxcode"],
                           shell=True)  # Windows


def init():
    get_workbench().add_view(LatextView, tr("Latext"), "se", visible_by_default=False)
