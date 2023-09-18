import sqlite3
import tkinter as tk
from tkinter import ttk

from thonny.exam import ExamListApp
from thonny.sqlite3_sql import ExamService, HomeworkService
from thonny.ui_utils import CommonDialog
from thonny.vendored_libs.score import scoreListApp


class homeworkAndExamDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master=master)
        ex_w = self.winfo_screenwidth()
        ex_h = self.winfo_screenheight()
        self.title("作业与考试")
        self.geometry("800x800+" + str(int(ex_w / 2) - 400) + "+" + str(int(ex_h / 2) - 400))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title_name = "我的作业"
        self.table_name = "t_homework"

        # 创建选项卡控件
        self.tabControl = ttk.Notebook(self)
        self.tabControl.pack(fill="both", expand=1)

        # 创建作业选项卡
        self.homework_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.homework_tab, text="作业")
        header_labels = ["作业序号", "作业名称", "作答时间（秒）", "作业简介"]
        for i, label in enumerate(header_labels):
            header_label = tk.Label(self.homework_tab, text=label, font=("bold", 12))
            header_label.grid(row=0, column=i, padx=10, pady=5, ipady=20, sticky="nsew")
            self.homework_tab.columnconfigure(1, weight=1)

        homework = HomeworkService()
        list1 = homework.list_homework()
        homework_list = []
        for item in list1:
            print("homework_list", item)
            homework_list.append(
                {
                    "id": item[0],
                    "name": item[1],
                    "time": item[4],
                    "description": item[6],
                    "question_id": item[7],
                }
            )

        ExamListApp(self.homework_tab, exam_list=homework_list, type="开始答题")

        # 创建考试选项卡
        self.exam_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.exam_tab, text="考试")

        header_labels = ["考试序号", "考试名称", "作答时间（秒）", "考试简介"]
        for i, label in enumerate(header_labels):
            header_label = tk.Label(self.exam_tab, text=label, font=("bold", 12))
            header_label.grid(row=0, column=i, padx=10, pady=5, ipady=20, sticky="nsew")
            self.exam_tab.columnconfigure(1, weight=1)

        exam_list = []
        exam = ExamService()
        list2 = exam.list_exam()
        for item in list2:
            exam_list.append(
                {
                    "id": item[0],
                    "name": item[1],
                    "time": item[4],
                    "description": item[6],
                    "question_id": item[7],
                }
            )

        ExamListApp(self.exam_tab, exam_list=exam_list, type="开始考试")

        # 创建作业成绩查询选项卡
        self.homework_score_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.homework_score_tab, text="作业成绩")

        header_labels = ["作业序号", "作业名称", "分数", "作答次数"]
        tk.Button(self.homework_score_tab, text="刷新", command=self.refreshWork).grid(row=0, pady=10)
        for i, label in enumerate(header_labels):
            header_label = tk.Label(self.homework_score_tab, text=label, font=("bold", 12))
            header_label.grid(row=1, column=i, padx=10, pady=5, ipady=30, sticky="nsew")
            self.homework_score_tab.columnconfigure(1, weight=1)

        homework_score_list = []
        homework_score = homework.list_homework_score()
        for item in homework_score:
            homework_score_list.append(
                {"id": item[0], "name": item[1], "score": item[5], "submit_count": item[6]}
            )

        scoreListApp(self.homework_score_tab, score_list=homework_score_list, type="查看详情")

        # 创建考试成绩查询选项卡
        self.exam_score_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.exam_score_tab, text="考试成绩")

        header_labels = ["作业序号", "作业名称", "分数", "作答次数"]
        tk.Button(self.exam_score_tab, text="刷新", command=self.refreshExam).grid(row=0, pady=10)
        for i, label in enumerate(header_labels):
            header_label = tk.Label(self.exam_score_tab, text=label, font=("bold", 12))
            header_label.grid(row=1, column=i, padx=10, pady=5, ipady=30, sticky="nsew")
            self.exam_score_tab.columnconfigure(1, weight=1)

        exam_score_list = []
        exam_score = exam.list_exam_score()
        for item in exam_score:
            exam_score_list.append(
                {"id": item[0], "name": item[1], "score": item[5], "submit_count": item[6]}
            )

        scoreListApp(self.exam_score_tab, score_list=exam_score_list, type="查看详情")

        # 为选项卡绑定事件
        self.tabControl.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_closing(self):
        self.destroy()  # 销毁窗口
    def refreshExam(self):
        exam = ExamService()
        exam_score_list = []
        exam_score = exam.list_exam_score()
        for item in exam_score:
            exam_score_list.append(
                {"id": item[0], "name": item[1], "score": item[5], "submit_count": item[6]}
            )
        scoreListApp(self.exam_score_tab, score_list=exam_score_list, type="查看详情")
    def refreshWork(self):
        homework = HomeworkService()
        homework_score_list = []
        homework_score = homework.list_homework_score()
        for item in homework_score:
            homework_score_list.append(
                {"id": item[0], "name": item[1], "score": item[5], "submit_count": item[6]}
            )
        scoreListApp(self.homework_score_tab, score_list=homework_score_list, type="查看详情")

    def on_tab_change(self, event):
        # print('我执行了')
        selected_tab = event.widget.select()
        tab_index = event.widget.index(selected_tab)

        if tab_index == 0:  # 作业选项卡
            self.show_data("HOMEWORK")
        elif tab_index == 1:  # 考试选项卡
            self.show_data("EXAM")

    def show_data(self, data_type):
        homework_service = HomeworkService()
        if data_type == "EXAM":
            self.table_name = "t_exam"
            self.title_name = "我的考试"
        data = homework_service.get_data(self.table_name)
        # self.show_tree_window(data)

    def show_tree_window(self, data):
        print(data)
        tree_window = tk.Toplevel(self)
        tree_window.title(self.title_name)
        tree_window.grab_set()
        tree = ttk.Treeview(tree_window)
        tree.heading("#0", text="名称")
        tree.pack()

        for item in data:
            tree.insert("", "end", text=item[0])
