import os
import sqlite3
from tkinter import messagebox
import requests
from contextlib import contextmanager

"""
sqlite单机数据库sql语句
NULL: 用于存储空值。

INTEGER: 用于存储整数，根据大小可分为：

TINYINT: 8 位整数
SMALLINT: 16 位整数
MEDIUMINT: 24 位整数
INT 或 INTEGER: 32 位整数
BIGINT: 64 位整数
REAL: 用于存储浮点数（双精度浮点数）。

VARCHAR(255): 用于存储文本字符串。

BLOB: 用于存储二进制数据，如图像、音频、视频等。

NUMERIC: 用于存储数字，可以包括整数和浮点数。
"""

# 定义表名
# 用户
user_table = "t_user"
# 视频
video_table = "t_video"
# 课程
course_table = "t_course"
# 课节
chapter_table = "t_chapter"
# 课时
section_table = "t_section"
# 作业
homework_table = "t_homework"
# 学员作业
homework_answer_log_table = "t_homework_answer_log"
# 考试
exam_table = "t_exam"
# 学员考试
exam_answer_log_table = "t_exam_answer_log"
# 题组
question_table = "t_question"
# 题目
stem_table = "t_stem"
# 题组题目
question_stem_table = "t_question_stem"
# 题目答案
answer_table = "t_answer"
# 用户成绩
user_score_table = "t_user_score"
# 用户课程
user_course_table = "t_user_course"

DATABASE_FILE = ""


def set_database(THONNY_USER_DIR):
    file_path = os.path.join(THONNY_USER_DIR, "database.db")
    # 创建目录（如果不存在）
    os.makedirs(os.path.dirname(THONNY_USER_DIR), exist_ok=True)
    if not os.path.exists(file_path):
        # 文件不存在，创建文件
        with open(file_path, "w") as file:
            pass
    global DATABASE_FILE
    DATABASE_FILE = file_path


@contextmanager
def open_sqlite_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()  # 在 try 块之外初始化 cursor
    try:
        cursor = conn.cursor()
        yield cursor  # 将游标传递给 with 语句块
        conn.commit()  # 在 with 语句块内执行 commit 操作
    except Exception as e:
        conn.rollback()  # 如果发生异常，执行回滚操作
        raise e
    finally:
        cursor.close()
        conn.close()


# 检查是否需要表初始化
def check_need_init():
    with open_sqlite_database() as cursor:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{user_table}'"
        cursor.execute(query)
        result = cursor.fetchone()
        if result is None or not result:
            return True
        else:
            return False


def data_init(account, password, user_type, course_type):
    with open_sqlite_database() as cursor:
        if not check_need_init():
            return
        # 初始化数据库表
        # 用户
        create_user_table_query = f"CREATE TABLE '{user_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, account VARCHAR(255), password VARCHAR(255), user_type VARCHAR(255), login_status INTEGER, origin_user_id INTEGER, version INTEGER)"
        cursor.execute(create_user_table_query)

        # 用户课程
        create_user_table_query = f"CREATE TABLE '{user_course_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_user_table_query)

        # 课程
        create_course_table_query = (
            f"CREATE TABLE '{course_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), course_describe VARCHAR(255), teacher_describe VARCHAR(255), price REAL, "
            f"section_num INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        )
        cursor.execute(create_course_table_query)
        # 课节
        create_chapter_table_query = f"CREATE TABLE '{chapter_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), course_id INTEGER, sort INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_chapter_table_query)
        # 课时
        create_section_table_query = f"CREATE TABLE '{section_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), chapter_id INTEGER, sort INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_section_table_query)
        # 视频
        create_video_table_query = f"CREATE TABLE '{video_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), path VARCHAR(255), section_id INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_video_table_query)
        # 视频路径检查
        # 题目
        create_stem_table_query = f"CREATE TABLE '{stem_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, content VARCHAR(255), `type` VARCHAR(255), score REAL, analysis VARCHAR(255), `level` TINYINT, enable INTEGER, is_delete INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_stem_table_query)
        # 题组
        create_question_table_query = f"CREATE TABLE '{question_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), type VARCHAR(255),enable INTEGER,is_delete INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_question_table_query)
        # 题目题组
        create_question_stem_table_query = f"CREATE TABLE '{question_stem_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER, stem_id INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_question_stem_table_query)
        # 题目答案
        create_answer_query = f"CREATE TABLE '{answer_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, content VARCHAR(255), stem_id INTEGER, is_correct INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        cursor.execute(create_answer_query)
        # 考试信息
        create_exam_table_query = (
            f"CREATE TABLE '{exam_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), submit_count INTEGER, display_answer_rule VARCHAR(255), answer_time INTEGER,"
            f" course_id INTEGER,description VARCHAR(255), question_id INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        )
        cursor.execute(create_exam_table_query)
        # 作业信息
        create_homework_table_query = (
            f"CREATE TABLE '{homework_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), submit_count INTEGER, display_answer_rule VARCHAR(255), answer_time INTEGER,"
            f" section_id INTEGER,description VARCHAR(255), question_id INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        )
        cursor.execute(create_homework_table_query)
        # 学员作业
        create_homework_answer_log_table_query = (
            f"CREATE TABLE '{homework_answer_log_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, homework_id INTEGER, stem_id INTEGER,"
            f" answer_ids VARCHAR(255), correct_answer_ids VARCHAR(255), user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        )
        cursor.execute(create_homework_answer_log_table_query)
        # 学员考试
        create_exam_answer_log_table_query = (
            f"CREATE TABLE '{exam_answer_log_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, exam_id INTEGER, stem_id INTEGER, answer_ids VARCHAR(255),"
            f" correct_answer_ids VARCHAR(255), user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        )
        cursor.execute(create_exam_answer_log_table_query)
        # 学员考试
        create_user_score_table_query = (
            f"CREATE TABLE '{user_score_table}' (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type VARCHAR(255),"
            f" source_id INTEGER, score REAL, submit_count INTEGER, user_type VARCHAR(255), course_type VARCHAR(255), version INTEGER)"
        )
        cursor.execute(create_user_score_table_query)
        # 数据插入
        # 用户数据
        insert_user_sql = f"INSERT INTO '{user_table}' (id, account, password, user_type, login_status, version) VALUES (?, ?, ?, ?, ?, ?)"
        user_values = (1, account, password, user_type, 1, 0)
        cursor.execute(insert_user_sql, user_values)
        # 用户课程
        insert_user_course_sql = (
            f"INSERT INTO '{user_course_table}' (id, user_id, course_type, version) VALUES (?, ?, ?, ?)"
        )
        user_course_values = (1, 1, course_type, 0)
        cursor.execute(insert_user_course_sql, user_course_values)
        # 课程初始化
        insert_course_sql = f"INSERT INTO '{course_table}' (id, title, course_describe, teacher_describe, price, section_num, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        course_values = (1, course_type, "课程介绍", "主讲教师介绍", 300.00, 10, user_type, course_type, 0)
        cursor.execute(insert_course_sql, course_values)
        if course_type == "PYTHON" and user_type == "PRIMARY_AND_SECONDARY":
            # 课节初始化
            insert_chapter_sql = f"INSERT INTO '{chapter_table}' (id ,title, course_id, sort, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?)"
            chapter_values = [
                (1, "第一课节", 1, 0, user_type, course_type, 0),
                (2, "第二课节", 1, 0, user_type, course_type, 0),
                (3, "第三课节", 1, 0, user_type, course_type, 0),
            ]
            cursor.executemany(insert_chapter_sql, chapter_values)

            # 课时初始化
            insert_chapter_sql = f"INSERT INTO '{section_table}' (id, title, chapter_id, sort, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?)"
            chapter_values = [
                (1, "第一课节-第一课时", 1, 0, user_type, course_type, 0),
                (2, "第一课节-第二课时", 1, 0, user_type, course_type, 0),
                (3, "第一课节-第三课时", 1, 0, user_type, course_type, 0),
                (4, "第二课节-第一课时", 2, 0, user_type, course_type, 0),
                (5, "第二课节-第二课时", 2, 0, user_type, course_type, 0),
                (6, "第二课节-第三课时", 2, 0, user_type, course_type, 0),
            ]
            cursor.executemany(insert_chapter_sql, chapter_values)

            # 题目初始化
            insert_stem_sql = f"INSERT INTO '{stem_table}' (id, content, `type`, score,analysis, `level`, enable, is_delete, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            stem_values = [
                (1, "第1个题目", "SINGLE_CHOICE", 10.00, "题目答案解析", 2, 1, 0, user_type, course_type, 0),
                (2, "第2个题目", "MULTIPLE_CHOICE", 10.00, "题目答案解析", 2, 1, 0, user_type, course_type, 0),
                (3, "第3个题目", "JUDGE", 10.00, "题目答案解析", 2, 1, 0, user_type, course_type, 0),
                (4, "第4个题目", "OTHER", 10.00, "题目答案解析", 2, 1, 0, user_type, course_type, 0),
            ]
            cursor.executemany(insert_stem_sql, stem_values)
            # 答案初始化
            insert_answer_sql = f"INSERT INTO '{answer_table}' (id, content, stem_id, is_correct, user_type, course_type,version) VALUES (?, ?, ?, ?, ?, ?, ?)"
            answer_values = [
                (1, "单选答案1", 1, 1, user_type, course_type, 0),
                (2, "单选答案2", 1, 0, user_type, course_type, 0),
                (3, "单选答案3", 1, 0, user_type, course_type, 0),
                (4, "单选答案4", 1, 0, user_type, course_type, 0),
                (5, "多选答案1", 2, 1, user_type, course_type, 0),
                (6, "多选答案2", 2, 1, user_type, course_type, 0),
                (7, "多选答案3", 2, 0, user_type, course_type, 0),
                (8, "多选答案4", 2, 0, user_type, course_type, 0),
                (9, "正确", 3, 1, user_type, course_type, 0),
                (10, "错误", 3, 0, user_type, course_type, 0),
                (11, "正确", 0, 0, user_type, course_type, 0),
                (12, "错误", 0, 1, user_type, course_type, 0),
                (13, "其他答案4", 4, 1, user_type, course_type, 0),
                (14, "其他答案4", 4, 0, user_type, course_type, 0),
            ]
            cursor.executemany(insert_answer_sql, answer_values)

            # 题组初始化
            insert_question_sql = f"INSERT INTO '{question_table}' (id, title, type, enable,is_delete, user_type, course_type ,version) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            question_values = [
                (1, "作业题组", "HOMEWORK", 1, 0, user_type, course_type, 0),
                (2, "考试题组", "EXAM", 1, 0, user_type, course_type, 0),
            ]
            cursor.executemany(insert_question_sql, question_values)

            # 题组题目绑定
            insert_question_stem_sql = f"INSERT INTO '{question_stem_table}' (id, question_id, stem_id, user_type, course_type,version) VALUES (?, ?, ?, ?, ?, ?)"
            question_stem_values = [
                (1, 1, 1, user_type, course_type, 0),
                (2, 1, 2, user_type, course_type, 0),
                (3, 1, 3, user_type, course_type, 0),
                (4, 1, 4, user_type, course_type, 0),
                (5, 2, 1, user_type, course_type, 0),
                (6, 2, 2, user_type, course_type, 0),
                (7, 2, 3, user_type, course_type, 0),
                (8, 2, 4, user_type, course_type, 0),
            ]
            cursor.executemany(insert_question_stem_sql, question_stem_values)

            # 初始化作业
            insert_homework_sql = f"INSERT INTO '{homework_table}' (id, name, submit_count, display_answer_rule, answer_time, section_id, description, question_id, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            homework_values = (1, "课时作业", 3, "DISPLAY", 3600, 1, "作业介绍", 1, user_type, course_type, 0)
            cursor.execute(insert_homework_sql, homework_values)

            # 初始化考试
            insert_exam_sql = f"INSERT INTO '{exam_table}' (id, name, submit_count, display_answer_rule, answer_time, course_id, description, question_id, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            exam_values = (1, "课程考试", 3, "DISPLAY", 3600, 1, "考试介绍", 1, user_type, course_type, 0)
            cursor.execute(insert_exam_sql, exam_values)

            # 初始化视频
            insert_video_sql = f"INSERT INTO '{video_table}' (id, name, path, section_id, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?)"
            video_values = [
                (1, "课时1视频", "/video/python/first/01.avi", 1, user_type, course_type, 0),
                (2, "课时2视频", "/video/python/first/8月20日技术分享视频.avi", 2, user_type, course_type, 0),
                (3, "课时3视频", "/video/python/first/02.avi", 3, user_type, course_type, 0),
            ]
            cursor.executemany(insert_video_sql, video_values)


class UserService:
    def __init__(self):
        self.is_first_login = True
        self.is_login = False

    def check_first_login(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT COUNT(*) FROM '{user_table}'"
            cursor.execute(query_sql)
            result = cursor.fetchone()
            existUser = result[0]
            if existUser <= 0:
                self.is_first_login = True
            else:
                self.is_first_login = False
            return self.is_first_login

    def login(self, account, password):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT COUNT(*) FROM '{user_table}' WHERE account = '{account}' AND password = '{password}'"
            cursor.execute(query_sql)
            result = cursor.fetchone()
            existUser = result[0]
            if existUser > 0:
                self.is_login = True
                return self.is_login

    def get_one(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{user_table}'"
            cursor.execute(query_sql)
            return cursor.fetchone()

    def list_user(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{user_table}'"
            cursor.execute(query_sql)
            return cursor.fetchall()

    def update_user(self, origin_user_id, user_id):
        with open_sqlite_database() as cursor:
            update_sql = f"UPDATE '{user_table}' SET origin_user_id = ? WHERE id = ?"
            update_values = (origin_user_id, user_id)
            cursor.execute(update_sql, update_values)


class UserCourseService:
    def get_one(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{user_course_table}'"
            cursor.execute(query_sql)
            return cursor.fetchone()

    def list_user_course(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{user_course_table}'"
            cursor.execute(query_sql)
            return cursor.fetchall()


def origin_update_homework(homeworks):
    with open_sqlite_database() as cursor:
        # 数据拼接
        insert_values = []
        for homework in homeworks:
            insert_value = (
                homework["id"],
                homework["name"],
                homework["submit_count"],
                homework["display_answer_rule"],
                homework["answer_time"],
                homework["section_id"],
                homework["description"],
                homework["question_id"],
                homework["user_type"],
                homework["course_type"],
                homework["version"],
            )
            insert_values.append(insert_value)

        # 移除原本地数据
        delete_sql = f"DELETE FROM '{homework_table}'"
        cursor.execute(delete_sql)

        insert_sql = (
            f"INSERT INTO '{homework_table}' (id, name, submit_count, display_answer_rule, "
            f"answer_time, section_id, description, question_id, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        cursor.executemany(insert_sql, insert_values)


class HomeworkService:
    def __init__(self):
        self.one = None

    # 作业列表
    def list_homework(self, homework_name=None, section_id=None):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{homework_table}'"

            if homework_name is not None:
                query_sql += f" WHERE name LIKE '%{homework_name}%'"
            if section_id is not None:
                if "WHERE" in query_sql:
                    query_sql += f" AND section_id = {section_id}"
                else:
                    query_sql += f" WHERE section_id = {section_id}"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    # 作业分数列表
    def list_homework_score(self):
        with open_sqlite_database() as cursor:
            query_sql = (
                f"SELECT h.id,h.name,h.submit_count,h.display_answer_rule,h.answer_time,us.score,us.submit_count "
                f"FROM '{user_score_table}' AS us "
                f"LEFT JOIN '{homework_table}' h ON h.id = us.source_id "
                f"WHERE us.type = 'HOMEWORK'  "
            )

            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    def get_data(self, table_name):
        with open_sqlite_database() as cursor:
            cursor.execute(f"SELECT name FROM '{table_name}'")
            data = cursor.fetchall()
            return data


class ExamService:
    def __init__(self):
        self.one = None

    # 考试列表
    def list_exam(self, exam_name=None, course_id=None):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{exam_table}'"
            if exam_name is not None:
                query_sql += f" WHERE name LIKE '%{exam_name}%'"
            if course_id is not None:
                if "WHERE" in query_sql:
                    query_sql += f" AND course_id = {course_id}"
                else:
                    query_sql += f" WHERE course_id = {course_id}"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    # 考试分数列表
    def list_exam_score(self):
        with open_sqlite_database() as cursor:
            query_sql = (
                f"SELECT e.id,e.name,e.submit_count,e.display_answer_rule,e.answer_time,us.score,us.submit_count "
                f"FROM '{user_score_table}' AS us "
                f"LEFT JOIN '{exam_table}' e ON e.id = us.source_id "
                f"WHERE us.type = 'EXAM'  "
            )

            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    def origin_update_exam(self, exams):
        with open_sqlite_database() as cursor:
            # 数据拼接
            insert_values = []
            for exam in exams:
                insert_value = (
                    exam["id"],
                    exam["name"],
                    exam["submit_count"],
                    exam["display_answer_rule"],
                    exam["answer_time"],
                    exam["course_id"],
                    exam["description"],
                    exam["question_id"],
                    exam["user_type"],
                    exam["course_type"],
                    exam["version"],
                )
                insert_values.append(insert_value)

            # 移除原本地数据
            delete_sql = f"DELETE FROM '{exam_table}'"
            cursor.execute(delete_sql)

            insert_sql = (
                f"INSERT INTO '{exam_table}' (id, name, submit_count, display_answer_rule, "
                f"answer_time, course_id, description, question_id, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)"
            )
            cursor.executemany(insert_sql, insert_values)


class QuestionService:
    def __init__(self):
        self.one = None

    # 题目详情
    def question_detail(self, question_id):
        with open_sqlite_database() as cursor:
            query_stem_sql = (
                f"SELECT s.id,s.content,s.type,s.score,s.level FROM '{question_table}' AS q "
                f"LEFT JOIN '{question_stem_table}' AS qs ON q.id = qs.question_id "
                f"LEFT JOIN '{stem_table}' AS s ON s.id = qs.stem_id "
                f"WHERE q.id = '{question_id}' "
                f"AND q.enable = 1 AND q.is_delete = 0"
            )

            cursor.execute(query_stem_sql)
            questions = cursor.fetchall()

            query_answer_sql = (
                f"SELECT a.id,a.content,a.stem_id,a.is_correct FROM '{question_table}' AS q "
                f"LEFT JOIN '{question_stem_table}' AS qs ON q.id = qs.question_id "
                f"LEFT JOIN '{answer_table}' AS a ON a.stem_id = qs.stem_id "
                f"WHERE q.id = '{question_id}' "
                f"AND q.enable = 1 AND q.is_delete = 0"
            )
            cursor.execute(query_answer_sql)
            answers = cursor.fetchall()

            merged_questions = []
            answers_dict = {}

            # 构建字典，以题目ID为键，对应的答案列表为值
            for answer in answers:
                stem_id = answer[2]
                if stem_id not in answers_dict:
                    answers_dict[stem_id] = []
                answers_dict[stem_id].append(answer)

            # 合并题目和答案
            for question in questions:
                stem_id = question[0]
                merged_question = list(question)
                merged_question.insert(4, answers_dict.get(stem_id, []))
                merged_questions.append(tuple(merged_question))

            return merged_questions

    # 查询提交次数
    def query_submit_count(self, type, source_id):
        with open_sqlite_database() as cursor:
            """
            type: EXAM  HOMEWORK
            source_id: 作业或考试ID
            """
            user_id = 1
            # 查询提交次数
            query_sql = (
                f"SELECT COUNT(*) FROM '{user_score_table}' WHERE user_id = {user_id} "
                f"AND type = {type} AND source_id = {source_id}  "
            )
            cursor.execute(query_sql)
            result = cursor.fetchone()
            submit_count = result[0]
            return submit_count

    # 提交考试答题
    def save_exam_answers(self, exam_answers):
        with open_sqlite_database() as cursor:
            """
            1，保存答题记录，
            2，计算此次分数，
            3，保存分数
            """
            # 考试ID
            exam_id = exam_answers["exam_id"]
            # 用户ID
            user_id = 0
            user_service = UserService()
            user = user_service.get_one()
            if user:
                user_id = user[0]
            else:
                messagebox.showinfo("提示", f"未查询到用户信息")
                return

            # 查询提交次数
            query_sql = (
                f"SELECT COUNT(*) FROM '{user_score_table}' WHERE user_id = {user_id} "
                f"AND type = 'EXAM' AND source_id = {exam_id}  "
            )
            cursor.execute(query_sql)
            result = cursor.fetchone()
            submit_count = result[0] + 1

            if exam_answers["stems"] is not None:
                exam_score = 0.0
                exam_answer_log_values = []
                for stem in exam_answers["stems"]:
                    # 答题记录封装
                    exam_answer_log_value = (
                        user_id,
                        exam_id,
                        stem["stem_id"],
                        stem["answer_ids"],
                        stem["correct_answer_ids"],
                        0,
                    )
                    exam_answer_log_values.append(exam_answer_log_value)
                    # 2,计算此次分数
                    # if stem['stem_type'] == "SINGLE_CHOICE":

                    if stem["answer_ids"] == stem["correct_answer_ids"]:
                        exam_score += stem["stem_score"]
                    # elif stem['stem_type'] == "MULTIPLE_CHOICE":
                    #     print()
                    # elif stem['stem_type'] == "JUDGE":
                    #     print()
                    # elif stem['stem_type'] == "OTHER":
                    #     print()
                    # else:
                    #     print("该类型暂无处理方式")

                # 1.1,删除之前的答题记录，
                delete_query = (
                    f"DELETE FROM '{exam_answer_log_table}' WHERE user_id = {user_id} "
                    f"AND exam_id={exam_id}"
                )
                cursor.execute(delete_query)
                # 1.2,保存这次答题记录
                insert_exam_answer_log_sql = (
                    f"INSERT INTO '{exam_answer_log_table}' "
                    f"(user_id, exam_id, stem_id, "
                    f"answer_ids, correct_answer_ids, version "
                    f") VALUES (?, ?, ?, ?, ?, ?)"
                )
                cursor.executemany(insert_exam_answer_log_sql, exam_answer_log_values)
                # 3，保存分数
                user_score_value = (user_id, "EXAM", exam_id, exam_score, submit_count, 0)
                insert_user_score_sql = (
                    f"INSERT INTO '{user_score_table}' "
                    f"(user_id, 'type', source_id, "
                    f"score, submit_count, version "
                    f") VALUES (?, ?, ?, ?, ?, ?)"
                )
                cursor.execute(insert_user_score_sql, user_score_value)

    # 提交作业答题
    def save_homework_answers(self, homework_answers):
        with open_sqlite_database() as cursor:
            """
                    1，保存答题记录，
                    2，计算此次分数，
                    3，保存分数
                    """
            # 作业ID
            homework_id = homework_answers["homework_id"]
            # 用户ID
            user_id = 0
            user_service = UserService()
            user = user_service.get_one()
            if user:
                user_id = user[0]
            else:
                messagebox.showinfo("提示", f"未查询到用户信息")
                return
            # 查询提交次数
            query_sql = (
                f"SELECT COUNT(*) FROM '{user_score_table}' WHERE user_id = {user_id} "
                f"AND type = 'HOMEWORK' AND source_id = {homework_id}  "
            )
            cursor.execute(query_sql)
            result = cursor.fetchone()
            submit_count = result[0] + 1

            if homework_answers["stems"] is not None:
                homework_score = 0.0
                homework_answer_log_values = []
                for stem in homework_answers["stems"]:
                    print(stem)
                    # 答题记录封装
                    homework_answer_log_value = (
                        user_id,
                        homework_id,
                        stem["stem_id"],
                        stem["answer_ids"],
                        stem["correct_answer_ids"],
                        0,
                    )
                    homework_answer_log_values.append(homework_answer_log_value)
                    # 2,计算此次分数
                    if stem["answer_ids"] == stem["correct_answer_ids"]:
                        homework_score += stem["stem_score"]

                # 1.1,删除之前的答题记录，
                delete_query = (
                    f"DELETE FROM '{homework_answer_log_table}' WHERE user_id = {user_id} "
                    f"AND homework_id={homework_id}"
                )
                cursor.execute(delete_query)
                # 1.2,保存这次答题记录
                insert_exam_answer_log_sql = (
                    f"INSERT INTO '{homework_answer_log_table}' "
                    f"(user_id, homework_id, stem_id, "
                    f"answer_ids, correct_answer_ids, version "
                    f") VALUES (?, ?, ?, ?, ?, ?)"
                )
                cursor.executemany(insert_exam_answer_log_sql, homework_answer_log_values)
                # 3，保存分数
                user_score_value = (user_id, "HOMEWORK", homework_id, homework_score, submit_count, 0)
                insert_user_score_sql = (
                    f"INSERT INTO '{user_score_table}' "
                    f"(user_id, 'type', source_id, "
                    f"score, submit_count, version "
                    f") VALUES (?, ?, ?, ?, ?, ?)"
                )
                cursor.execute(insert_user_score_sql, user_score_value)

    def origin_update_question(self, questions):
        with open_sqlite_database() as cursor:
            # 数据拼接
            insert_values = []
            for question in questions:
                insert_value = (
                    question["id"],
                    question["title"],
                    question["type"],
                    question["enable"],
                    question["is_delete"],
                    question["user_type"],
                    question["course_type"],
                    question["version"],
                )
                insert_values.append(insert_value)

            # 移除原本地数据
            delete_sql = f"DELETE FROM '{question_table}'"
            cursor.execute(delete_sql)

            insert_sql = f"INSERT INTO '{question_table}' (id, title, type, enable,is_delete, user_type, course_type ,version) VALUES (?, ?, ?, ?, ?, ?,?,?)"
            cursor.executemany(insert_sql, insert_values)


class VideoService:
    def list_video(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{video_table}'"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    def origin_update_video(self, videos):
        with open_sqlite_database() as cursor:
            # 数据拼接
            insert_values = []
            for video in videos:
                video_url = video["path"]
                save_path = os.path.join(
                    os.path.dirname(__file__), "video", video["course_type"], video["name"]
                )

                # 发送HTTP请求获取视频内容
                response = requests.get(video_url, stream=True)

                # 确保请求成功
                if response.status_code == 200:
                    # 以二进制写入方式打开文件，并逐块写入内容
                    with open(save_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("视频下载完成")
                else:
                    print("视频下载失败")

                insert_video_value = (
                    video["id"],
                    video["name"],
                    save_path,
                    video["section_id"],
                    video["user_type"],
                    video["course_type"],
                    video["version"],
                )
                insert_values.append(insert_video_value)

            # 移除本地视频

            # 移除原本地数据
            delete_sql = f"DELETE FROM '{video_table}'"
            cursor.execute(delete_sql)

            insert_sql = f"INSERT INTO '{video_table}' (id, name, path, section_id, user_type, course_type, version) VALUES (?, ?, ?, ?, ?,?,?)"
            cursor.executemany(insert_sql, insert_values)


class StemService:
    def list_stem(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{stem_table}'"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    def origin_update_stem(self, stems):
        with open_sqlite_database() as cursor:
            # 数据拼接
            insert_values = []
            for stem in stems:
                insert_value = (
                    stem["id"],
                    stem["content"],
                    stem["type"],
                    float(stem["score"]),
                    stem["analysis"],
                    stem["level"],
                    stem["enable"],
                    stem["is_delete"],
                    stem["user_type"],
                    stem["course_type"],
                    stem["version"],
                )
                insert_values.append(insert_value)

            # 移除原本地数据
            delete_sql = f"DELETE FROM '{stem_table}'"
            cursor.execute(delete_sql)

            insert_sql = (
                f"INSERT INTO '{stem_table}' (id, content, `type`, score,analysis, `level`, enable, "
                f"is_delete, user_type, course_type, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)"
            )
            cursor.executemany(insert_sql, insert_values)


class AnswerService:
    def list_answer(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{stem_table}'"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    def origin_update_answer(self, answers):
        with open_sqlite_database() as cursor:
            # 数据拼接
            insert_values = []
            for answer in answers:
                insert_value = (
                    answer["id"],
                    answer["content"],
                    answer["stem_id"],
                    answer["is_correct"],
                    answer["user_type"],
                    answer["course_type"],
                    answer["version"],
                )
                insert_values.append(insert_value)

            # 移除原本地数据
            delete_sql = f"DELETE FROM '{answer_table}'"
            cursor.execute(delete_sql)

            insert_sql = f"INSERT INTO '{answer_table}' (id, content, stem_id, is_correct, user_type, course_type,version) VALUES (?, ?, ?, ?, ?,?,?)"
            cursor.executemany(insert_sql, insert_values)


class QuestionStemService:
    def list_question_stem(self):
        with open_sqlite_database() as cursor:
            query_sql = f"SELECT * FROM '{question_stem_table}'"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            return result

    def origin_update_question_stem(self, question_stems):
        with open_sqlite_database() as cursor:
            # 数据拼接
            insert_values = []
            for question_stem in question_stems:
                insert_value = (
                    question_stem["id"],
                    question_stem["question_id"],
                    question_stem["stem_id"],
                    question_stem["user_type"],
                    question_stem["course_type"],
                    question_stem["version"],
                )
                insert_values.append(insert_value)

            # 移除原本地数据
            delete_sql = f"DELETE FROM '{question_stem_table}'"
            cursor.execute(delete_sql)

            insert_sql = f"INSERT INTO '{question_stem_table}' (id, question_id, stem_id, user_type, course_type,version) VALUES (?, ?, ?, ?,?,?)"
            cursor.executemany(insert_sql, insert_values)
