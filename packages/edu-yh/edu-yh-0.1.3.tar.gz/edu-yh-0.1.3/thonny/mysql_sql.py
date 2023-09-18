import mysql.connector.pooling

"""
远端服务器mysql连接

基本操作示例，自行修改逻辑
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

version_update_table = "t_version_update"

# 创建MySQL连接池
config = {
    "user": "root",
    "password": "aY)I&iBop[F3t",
    "host": "180.76.235.69",
    "port": "3306",
    "database": "thonny",
    "auth_plugin": "mysql_native_password",
}

db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **config)


# 开启连接
def open_connection():
    # 创建数据库连接
    db_connection = db_pool.get_connection()
    return db_connection


# 关闭连接
def close_connection(cursor, db_connection):
    # 关闭游标和连接
    cursor.close()
    db_connection.close()


class IUpdateVersion:
    def check_update_version(self, user_type, course_array):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)
        placeholders = ", ".join(["%s"] * len(course_array))

        select_sql = f"SELECT * FROM {version_update_table} WHERE user_type = %s AND course_type IN ({placeholders}) AND update_status = 1"

        query_value = [user_type] + course_array
        cursor.execute(select_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


# 检查版本号
class IUserService:
    def __init__(self):
        self.is_first_login = True
        self.is_login = False

    def insert_user(self, user):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)
        account = user[1]
        password = user[2]
        user_type = user[3]
        login_status = user[4]
        version = user[6]
        insert_user_sql = f"INSERT INTO {user_table} (account, password, user_type, login_status, version) VALUES (%s, %s, %s, %s, %s)"
        user_values = (account, password, user_type, login_status, version)
        cursor.execute(insert_user_sql, user_values)
        db_connection.commit()
        # 获取插入数据的自增 ID
        last_row_id = cursor.lastrowid
        close_connection(cursor, db_connection)
        return last_row_id

    def list_user(self):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)
        query_sql = f"SELECT * FROM {user_table}"
        cursor.execute(query_sql)
        fetchone = cursor.fetchone()
        close_connection(cursor, db_connection)
        return fetchone


class IHomeworkService:
    def __init__(self):
        self.one = None

    def list_homework(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {homework_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


class IExamService:
    def __init__(self):
        self.one = None

    def list_exam(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {exam_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


class IQuestionService:
    def __init__(self):
        self.one = None

    # 题目详情
    def list_question(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {question_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


class IVideoService:
    def list_video(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {video_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


class IStemService:
    def list_stem(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {stem_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


class IAnswerService:
    def list_answer(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {answer_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result


class IQuestionStemService:
    def list_question_stem(self, user_type, course_type):
        db_connection = open_connection()
        cursor = db_connection.cursor(dictionary=True)

        # 构建完整的查询语句
        query_sql = f"SELECT * FROM {question_stem_table} WHERE user_type = %s AND course_type = %s"

        # 构建查询参数，注意首先加入 user_type 参数，然后加入 course_type 中的各个值
        query_value = (user_type, course_type)
        cursor.execute(query_sql, query_value)
        result = cursor.fetchall()
        close_connection(cursor, db_connection)
        return result
