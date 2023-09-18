import tkinter as tk
from tkinter import messagebox, ttk

from thonny.sqlite3_sql import QuestionService


class ExamDetailsPage:
    def __init__(self, root, questions, exam_id, type, time):
        self.root = root
        self.questions = questions
        self.exam_id = exam_id
        self.type = type
        self.time = time

        # 创建题目数组
        # self.questions = [
        #     {"id": 1, "type": "SINGLE_CHOICE", "title": "问题1", "options": ["选项1", "选项2", "选项3", "选项4"]},
        #     {"id": 2, "type": "MULTIPLE_CHOICE", "title": "问题2", "options": ["选项1", "选项2", "选项3", "选项4"]},
        #     {"id": 3, "type": "JUDGE", "title": "问题3", "options": ["正确", "错误"]},
        #     {"id": 5, "type": "SINGLE_CHOICE", "title": "问题5", "options": ["选项1", "选项2", "选项3", "选项4"]},
        #     {"id": 6, "type": "MULTIPLE_CHOICE", "title": "问题6", "options": ["选项1", "选项2", "选项3", "选项4"]}
        # ]

        # 创建控件
        self.exam_title_label = tk.Label(self.root, text="试卷标题")  # 试卷标题标签
        self.exam_title_label.pack()

        self.total_score_label = tk.Label(self.root, text="总分：100")  # 总分标签
        self.total_score_label.pack()

        self.passing_score_label = tk.Label(self.root, text="及格分数：60")  # 及格分数标签
        self.passing_score_label.pack()

        self.exam_time_label = tk.Label(
            self.root, text="考试时间：" + str(self.time / 60) + "分钟"
        )  # 考试时间标签
        self.exam_time_label.pack()

        self.total_seconds = self.time
        # self.total_seconds = 5
        self.hours = 0  # 时
        self.minutes = 0  # 分
        self.seconds = 0  # 秒

        self.countdown_label = tk.Label(self.root, text="考试结束倒计时: ")
        self.countdown_label.pack()
        self.run()

        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建 Canvas
        self.canvas = tk.Canvas(self.root, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        self.scrollbar.config(command=self.canvas.yview)

        self.question_frame = tk.Frame(self.canvas, highlightthickness=0)

        self.canvas.create_window((0, 0), window=self.question_frame, anchor=tk.NW)

        self.questions_labels = []  # 题目标签列表
        self.radio_vars = []  # SINGLE_CHOICE题选项变量列表
        self.determine = []  # JUDGE题选项变量列表
        self.check_vars = []  # MULTIPLE_CHOICE题选项变量列表

        # self.res

        for question in self.questions:
            question_label = tk.Label(
                self.question_frame,
                text=f"{self.top_ic_type(question['type'])}题目：{question['title']},分值：{question['fraction']}, 难度：{str(question['difficulty']) + '颗星'}",
            )
            question_label.pack(anchor="w", fill="x")
            self.questions_labels.append(question_label)

            if question["type"] == "SINGLE_CHOICE" or question["type"] == "MULTIPLE_CHOICE":
                label_frame = tk.Frame(self.question_frame)  # 标签框架
                label_frame.pack(anchor="w", fill="x", padx=10)

                options_frame = tk.Frame(label_frame)  # 选项框架
                options_frame.pack(side=tk.LEFT)

                if question["type"] == "SINGLE_CHOICE":
                    radio_var = tk.IntVar()  # SINGLE_CHOICE题选项变量
                    self.radio_vars.append(radio_var)

                    for index, option in enumerate(question["options"]):
                        option_radio = tk.Radiobutton(
                            options_frame, text=option[1], variable=radio_var, value=index + 1
                        )
                        option_radio.pack(anchor="w", fill="x", padx=10)
                elif question["type"] == "MULTIPLE_CHOICE":
                    check_vars_list = []  # MULTIPLE_CHOICE题选项变量列表
                    for i, option in enumerate(question["options"]):
                        check_var = tk.IntVar()  # MULTIPLE_CHOICE题选项变量
                        check_vars_list.append(check_var)
                        option_check = tk.Checkbutton(
                            options_frame, text=option[1], variable=check_var
                        )
                        option_check.pack(anchor="w", fill="x", padx=10)
                    self.check_vars.append(check_vars_list)

            elif question["type"] == "JUDGE":
                judge_var = tk.IntVar()  # JUDGE题选项变量

                for item in question["options"]:
                    option_radio1 = tk.Radiobutton(
                        self.question_frame, text=item[1], variable=judge_var, value=item[0]
                    )
                    option_radio1.pack(anchor="w", fill="x", padx=10)

                self.determine.append(judge_var)

        self.submit_button = tk.Button(self.root, text="提交", command=self.submit_exam)  # 提交按钮
        self.submit_button.pack(pady=20)

        self.question_frame.bind("<Configure>", self.on_frame_configure)

    def start_countdown(self):
        if self.total_seconds > 0:
            self.calculate_time()

            self.countdown_label[
                "text"
            ] = f"考试结束倒计时: {self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"

            self.total_seconds -= 1
            self.root.after(1000, self.start_countdown)
        else:
            messagebox.showinfo("考试结束", "时间到了！")
            self.submit_exam()

    def calculate_time(self):
        self.hours = self.total_seconds // 3600
        self.minutes = (self.total_seconds % 3600) // 60
        self.seconds = self.total_seconds % 60

    def run(self):
        self.start_countdown()

    def top_ic_type(self, type):
        if type == "SINGLE_CHOICE":
            return "单选题: "
        elif type == "MULTIPLE_CHOICE":
            return "多选题: "
        elif type == "JUDGE":
            return "判断题: "
        else:
            return "未知类型题目: "

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def submit_exam(self):
        request_arr = []
        # SINGLE_CHOICE开始下标
        radio_index = 0
        # MULTIPLE_CHOICE开始下标
        checkbox_index = 0
        # JUDGE开始下标
        determine_index = 0
        for index, question in enumerate(self.questions):
            question_id = question["id"]
            question_type = question["type"]
            if question_type == "SINGLE_CHOICE":
                selected_option = question["options"][self.radio_vars[radio_index].get() - 1]
                radio_index += 1
                request_arr.append(
                    {
                        "question_id": "题目id" + str(question_id),
                        "type": "SINGLE_CHOICE",
                        "user_select": selected_option,
                        "source": question,
                    }
                )
            elif question_type == "MULTIPLE_CHOICE":
                temp_dx = 0
                tempArr = []
                for item in self.check_vars[checkbox_index]:
                    if item.get() == 1:
                        tempArr.append(question["options"][temp_dx])
                    temp_dx += 1
                request_arr.append(
                    {
                        "question_id": "题目id" + str(question_id),
                        "type": "MULTIPLE_CHOICE",
                        "user_select": tempArr,
                        "source": question,
                    }
                )
                checkbox_index += 1
            elif question_type == "JUDGE":
                self.determine[determine_index].get()
                request_arr.append(
                    {
                        "question_id": "题目id" + str(question_id),
                        "type": "JUDGE",
                        "user_select": self.determine[determine_index].get(),
                        "source": question,
                    }
                )
                determine_index += 1
        temp_req_arr = []
        for item in request_arr:
            print(item)
            temp = item["source"]
            res = temp["correct"]
            str_list = [str(num) for num in res]
            answer_ids = ",".join(str_list)
            user_select_arr = []
            if type(item["user_select"]) == list:
                for i in item["user_select"]:
                    user_select_arr.append(i[0])
                str_user_list = [str(num) for num in user_select_arr]
                user_select = ",".join(str_user_list)
            elif type(item["user_select"]) == tuple:
                user_select = str(item["user_select"][0])
            else:
                temp
                user_select = str(item["user_select"])
            temp_req_arr.append(
                {
                    "stem_id": temp["id"],
                    "stem_type": temp["type"],
                    "stem_score": temp["fraction"],
                    "answer_ids": user_select,
                    "correct_answer_ids": answer_ids,
                }
            )

        qus = QuestionService()
        if self.type == "开始考试":
            request_obj = {"exam_id": self.exam_id, "stems": temp_req_arr}
            qus.save_exam_answers(request_obj)
            messagebox.showinfo("成功", "提交成功")
        else:
            request_obj = {"homework_id": self.exam_id, "stems": temp_req_arr}
            qus.save_homework_answers(request_obj)
            messagebox.showinfo("成功", "提交成功")
        self.root.destroy()
