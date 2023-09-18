# -*- coding: utf-8 -*-

import datetime
import platform
import sys
import tkinter as tk
import tkinter.font
from logging import getLogger
from tkinter import messagebox, ttk

from thonny.utils.internet_utils import InternetUtil

import thonny
from thonny import get_workbench, ui_utils
from thonny.common import get_python_version_string
from thonny.languages import tr
from thonny.mysql_sql import (
    IAnswerService,
    IExamService,
    IHomeworkService,
    IQuestionService,
    IQuestionStemService,
    IStemService,
    IUpdateVersion,
    IVideoService,
)
from thonny.sqlite3_sql import (
    AnswerService,
    ExamService,
    HomeworkService,
    QuestionService,
    QuestionStemService,
    StemService,
    UserCourseService,
    UserService,
    VideoService,
)
from thonny.ui_utils import CommonDialogEx, create_url_label

logger = getLogger(__name__)


# 定义了一个AboutDialog类，继承自CommonDialogEx类，
# 用于创建关于Thonny的对话框。对话框中包含了Thonny的版本号、官方网站链接、开发者信息、许可信息等内容。
class AboutDialog(CommonDialogEx):
    def __init__(self, master):
        super().__init__(master)

        self.title(tr("About Thonny"))  # 设置对话框标题
        self.resizable(height=tk.FALSE, width=tk.FALSE)  # 禁止调整对话框大小

        default_heading_font = tkinter.font.nametofont("TkHeadingFont")
        heading_font = default_heading_font.copy()
        heading_font.configure(size=int(default_heading_font["size"] * 1.7), weight="bold")
        heading_label = ttk.Label(
            self.main_frame, text="Thonny " + thonny.get_version(), font=heading_font
        )
        heading_label.grid(pady=(self.get_large_padding(), self.get_small_padding()))

        url_label = create_url_label(self.main_frame, "https://thonny.org", justify=tk.CENTER)
        url_label.grid()

        if sys.platform == "linux":
            try:
                import distro  # 不需要安装distro模块

                system_desc = distro.name(True)
            except ImportError:
                system_desc = "Linux"

            if "32" not in system_desc and "64" not in system_desc:
                system_desc += self.get_os_word_size_suffix()
        elif sys.platform == "darwin":
            mac_ver = platform.mac_ver()[0]
            mac_arch = platform.mac_ver()[2]
            system_desc = f"macOS {mac_ver} ({mac_arch})"
        else:
            release = platform.release()
            if sys.platform == "win32":
                # Win 10 and 11 both give 10 as release
                try:
                    build = int(platform.version().split(".")[2])
                    if release == "10" and build >= 22000:
                        release = "11"
                except Exception:
                    logger.exception("Could not determine Windows version")

            system_desc = platform.system() + " " + release + self.get_os_word_size_suffix()

        platform_label = ttk.Label(
            self.main_frame,
            justify=tk.CENTER,
            text=system_desc
            + "\n"
            + "Python "
            + get_python_version_string()
            + "\n"
            + "Tk "
            + ui_utils.get_tk_version_str(),
        )
        platform_label.grid(pady=self.get_medium_padding())

        credits_label = create_url_label(
            self.main_frame,
            "https://github.com/thonny/thonny/blob/master/CREDITS.rst",
            tr(
                "Made in\n"
                + "University of Tartu, Estonia,\n"
                + "with the help from\n"
                + "open-source community,\n"
                + "Raspberry Pi Foundation\n"
                + "and Cybernetica AS"
            ),
            justify=tk.CENTER,
        )
        credits_label.grid()

        default_font = tkinter.font.nametofont("TkDefaultFont")
        license_font = default_font.copy()
        license_font.configure(size=round(default_font["size"] * 0.7))
        license_label = ttk.Label(
            self.main_frame,
            text="Copyright (©) "
            + str(datetime.datetime.now().year)
            + " Aivar Annamaa\n"
            + tr(
                "This program comes with\n"
                + "ABSOLUTELY NO WARRANTY!\n"
                + "It is free software, and you are welcome to\n"
                + "redistribute it under certain conditions, see\n"
                + "https://opensource.org/licenses/MIT\n"
                + "for details"
            ),
            justify=tk.CENTER,
            font=license_font,
        )
        license_label.grid(pady=self.get_medium_padding())

        ok_button = ttk.Button(
            self.main_frame, text=tr("OK"), command=self.on_close, default="active"
        )
        ok_button.grid(pady=(0, self.get_large_padding()))
        ok_button.focus_set()

        self.bind("<Return>", self.on_close, True)

    def get_os_word_size_suffix(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return " (32-bit)"
        else:
            return ""


# load_plugin函数用于加载插件
def load_plugin() -> None:
    def _check_version_and_update():
        # 检查网络状况
        internet_util = InternetUtil()
        connection = internet_util.check_internet_connection()
        if not connection:
            messagebox.showerror("系统提示", "版本及数据更新失败，检测到未连接网络，请确认网络状态")
        else:
            print("版本更新")
            # 版本及数据对比
            # 对比表中每一个id相同的远程数据版本号和本地版本号是否一致，不一致，单独更新该条数据
            compare_data_count()

    def compare_data_count():
        user_service = UserService()
        user = user_service.get_one()
        # 用户信息
        user_type = user[3]
        user_course_service = UserCourseService()
        user_course_list = user_course_service.list_user_course()
        print(user_course_list)
        # 用户课程
        course_array = []
        for i, user_course in enumerate(user_course_list):
            course_array.insert(i, user_course[2])

        # 查询哪些表需要更新
        i_update_version = IUpdateVersion()
        update_versions = i_update_version.check_update_version(user_type, course_array)
        for update_version in update_versions:
            table_name_ = update_version["table_name"]
            course_type = update_version["course_type"]
            if table_name_ == thonny.mysql_sql.video_table:
                # 获取远程视频数据
                i_video_service = IVideoService()
                videos = i_video_service.list_video(user_type, course_type)
                # 比较本地视频数据并进行更新
                video_service = VideoService()
                video_service.origin_update_video(videos)
            elif table_name_ == thonny.mysql_sql.stem_table:
                # 获取远程题目数据
                i_stem_service = IStemService()
                stems = i_stem_service.list_stem(user_type, course_type)
                # 比较本地题目数据并进行更新
                stem_service = StemService()
                stem_service.origin_update_stem(stems)
            elif table_name_ == thonny.mysql_sql.answer_table:
                # 获取远程答案数据
                i_answer_service = IAnswerService()
                answers = i_answer_service.list_answer(user_type, course_type)
                # 比较本地答案数据并进行更新
                answer_service = AnswerService()
                answer_service.origin_update_answer(answers)
            elif table_name_ == thonny.mysql_sql.question_table:
                # 获取远程题组数据
                i_question_service = IQuestionService()
                questions = i_question_service.list_question(user_type, course_type)
                # 比较本地题组数据并进行更新
                question_service = QuestionService()
                question_service.origin_update_question(questions)
            elif table_name_ == thonny.mysql_sql.question_stem_table:
                # 获取远程题目题组数据
                i_question_stem_service = IQuestionStemService()
                question_stems = i_question_stem_service.list_question_stem(user_type, course_type)
                # 比较本地题目题组数据并进行更新
                question_stem_service = QuestionStemService()
                question_stem_service.origin_update_question_stem(question_stems)
            elif table_name_ == thonny.mysql_sql.homework_table:
                # 获取远程作业数据
                i_homework_service = IHomeworkService()
                homeworks = i_homework_service.list_homework(user_type, course_type)
                # 比较本地作业数据并进行更新
                homework_service = HomeworkService()
                homework_service.origin_update_homework(homeworks)
            elif table_name_ == thonny.mysql_sql.exam_table:
                # 获取远程考试数据
                i_exam_service = IExamService()
                exams = i_exam_service.list_exam(user_type, course_type)
                # 比较本地考试数据并进行更新
                exam_service = ExamService()
                exam_service.origin_update_exam(exams)

    def open_about():
        # 打开对话框
        ui_utils.show_dialog(AboutDialog(get_workbench()))

    def open_url(url):
        import webbrowser

        # webbrowser.open返回bool值，但add_command需要None值
        webbrowser.open(url)

    # 添加到下拉菜单help里  绑定命令：打开版本历史记录的链接
    get_workbench().add_command(
        "changelog",
        "help",
        tr("版本历史"),
        lambda: open_url("https://github.com/thonny/thonny/blob/master/CHANGELOG.rst"),
        group=60,
    )
    # 添加到下拉菜单help里 绑定命令：打开报告问题的链接
    get_workbench().add_command(
        "issues",
        "help",
        tr("报告问题"),
        lambda: open_url("https://github.com/thonny/thonny/issues"),
        group=60,
    )

    # 添加到下拉菜单help里 绑定命令：检查版本及数据更新
    get_workbench().add_command(
        "version",
        "help",
        tr("版本检查"),
        _check_version_and_update,
        group=60,
    )

    # 添加到下拉菜单help里：打开关于Thonny的对话框
    get_workbench().add_command("about", "help", tr("关于Thonny"), open_about, group=61)

    # For Mac
    get_workbench().createcommand("tkAboutDialog", open_about)
