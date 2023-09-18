from thonny.sqlite3_sql import ExamService, HomeworkService, QuestionService

#
homework = HomeworkService()
# list1 = homework.list_homework()
homework_score = homework.list_homework_score()
print(homework_score)
# #
# #
# exam = ExamService()
# list2 = exam.list_exam(course_id=2)
# #
# qus = QuestionService()
# # detail = qus.question_detail(1)
# # print(detail)
# exam_answers = {
#     "exam_id": 1,  # 考试ID
#     "stems": [  # 题目集
#         {
#             "stem_id": 1,  # 题目ID
#             "stem_type": "SINGLE_CHOICE",  # 题目类型
#             "stem_score": 10.0,  # 题目分数
#             "answer_ids": "1",  # 答案集
#             "correct_answer_ids": "1"  # 正确答案集
#         }, {
#             "stem_id": 2,  # 题目ID
#             "stem_type": "SINGLE_CHOICE",  # 题目类型
#             "stem_score": 10.0,  # 题目分数
#             "answer_ids": "5",  # 答案集
#             "correct_answer_ids": "6"  # 正确答案集
#         }, {
#             "stem_id": 3,  # 题目ID
#             "stem_type": "SINGLE_CHOICE",  # 题目类型
#             "stem_score": 10.0,  # 题目分数
#             "answer_ids": "10",  # 答案集
#             "correct_answer_ids": "11"  # 正确答案集
#         }
#     ]
# }
# qus.save_exam_answers(exam_answers)
# # homework_answers = {
# #     "homework_id": 1,  # 考试ID
# #     "stems": [  # 题目集
# #         {
# #             "stem_id": 1,  # 题目ID
# #             "stem_type": "SINGLE_CHOICE",  # 题目类型
# #             "stem_score": 10.0,  # 题目分数
# #             "answer_ids": "1",  # 答案集
# #             "correct_answer_ids": "1"  # 正确答案集
# #         }, {
# #             "stem_id": 2,  # 题目ID
# #             "stem_type": "SINGLE_CHOICE",  # 题目类型
# #             "stem_score": 10.0,  # 题目分数
# #             "answer_ids": "5",  # 答案集
# #             "correct_answer_ids": "6"  # 正确答案集
# #         }, {
# #             "stem_id": 3,  # 题目ID
# #             "stem_type": "SINGLE_CHOICE",  # 题目类型
# #             "stem_score": 10.0,  # 题目分数
# #             "answer_ids": "10",  # 答案集
# #             "correct_answer_ids": "11"  # 正确答案集
# #         }
# #     ]
# # }
# # qus.save_homework_answers(homework_answers)
# # submit_count = qus.query_submit_count("EXAM", 1)
# # print(submit_count)
# import tkinter as tk
# from tkinter import messagebox
#
# class CountdownTimer:
#     def __init__(self, total_seconds):
#         self.total_seconds = total_seconds
#         self.hours = 0
#         self.minutes = 0
#         self.seconds = 0
#
#         self.root = tk.Tk()
#         self.root.title("倒计时")
#         self.root.geometry("200x100")
#
#         self.countdown_label = tk.Label(self.root, text="倒计时: ")
#         self.countdown_label.pack()
#
#     def start_countdown(self):
#         if self.total_seconds > 0:
#             self.calculate_time()
#
#             self.countdown_label['text'] = f"倒计时: {self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
#
#             self.total_seconds -= 1
#             self.root.after(1000, self.start_countdown)
#         else:
#             messagebox.showinfo("倒计时完成", "时间到了！")
#
#     def calculate_time(self):
#         self.hours = self.total_seconds // 3600
#         self.minutes = (self.total_seconds % 3600) // 60
#         self.seconds = self.total_seconds % 60
#
#     def run(self):
#         self.start_countdown()
#         self.root.mainloop()
#
# # 创建一个倒计时器对象，设定倒计时的总秒数
# timer = CountdownTimer(3666)  # 示例倒计时总秒数
# timer.run()
