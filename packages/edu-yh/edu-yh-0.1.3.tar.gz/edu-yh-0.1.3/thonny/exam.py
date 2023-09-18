import tkinter as tk
from tkinter import messagebox, ttk

from thonny.exam_details import ExamDetailsPage
from thonny.sqlite3_sql import QuestionService


class ExamListApp:
    def __init__(self, root, exam_list, type):
        self.root = root
        self.exam_list = exam_list
        self.type = type
        self.create_exam_list()

    def create_exam_list(self):
        for i, exam in enumerate(self.exam_list):
            subject_label = tk.Label(self.root, text=exam["id"])
            subject_label.grid(row=i + 1, column=0, padx=5, pady=5)

            date_label = tk.Label(self.root, text=exam["name"])
            date_label.grid(row=i + 1, column=1, padx=10, pady=5)

            time_label = tk.Label(self.root, text=exam["time"])
            time_label.grid(row=i + 1, column=2, padx=5, pady=5)

            time_label = tk.Label(self.root, text=exam["description"])
            time_label.grid(row=i + 1, column=3, padx=10, pady=5)

            start_button = ttk.Button(
                self.root, text=self.type, command=lambda exam=exam: self.start_exam(exam)
            )
            start_button.grid(row=i + 1, column=4, padx=10, pady=5)

    def find_correct(self, options):
        tempArr = []
        for item in options:
            if item[3] == 1:
                tempArr.append(item[0])
        return tempArr

    def start_exam(self, exam):
        qus = QuestionService()

        goto_list = []
        detail = qus.question_detail(exam["question_id"])

        # {"id": 1, "type": "SINGLE_CHOICE", "title": "问题1", "options": ["选项1", "选项2", "选项3", "选项4"]},
        for item in detail:
            # print('后端返回', item)
            goto_list.append(
                {
                    "id": item[0],
                    "type": item[2],
                    "title": item[1],
                    "fraction": item[3],
                    "options": item[4],
                    "difficulty": item[5],
                    "correct": self.find_correct(item[4]),
                }
            )

        self.exam_details = tk.Toplevel(self.root)
        ex_w = self.exam_details.winfo_screenwidth()
        ex_h = self.exam_details.winfo_screenheight()
        self.exam_details.grab_set()
        self.exam_details.title("详情")
        # 绑定窗口关闭事件
        self.exam_details.protocol("WM_DELETE_WINDOW", self.on_exam_details_close)
        self.exam_details.geometry(
            "600x600+" + str(int(ex_w / 2) - 300) + "+" + str(int(ex_h / 2) - 300)
        )
        ExamDetailsPage(
            self.exam_details,
            questions=goto_list,
            exam_id=exam["id"],
            type=self.type,
            time=exam["time"],
        )

    def on_exam_details_close(self):
        # 弹出确认对话框
        if messagebox.askokcancel("退出", "确定要关闭吗,关闭题目不保存哦？"):
            # 用户点击确定，关闭窗口
            self.exam_details.destroy()


# if __name__ == '__main__':
#     root = tk.Tk()
#     root.title("考试列表")
#
#     header_labels = ['科目', '日期', '时间']
#     for i, label in enumerate(header_labels):
#         header_label = tk.Label(root, text=label, font=('bold', 12))
#         header_label.grid(row=0, column=i, padx=10, pady=5)
#
#     app = ExamListApp(root)
#
#     root.mainloop()
