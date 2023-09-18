import json
import requests

from thonny.utils.HttpUtils import HttpUtil

"""
曙光接口工具类
"""


# 提交作业参数封装类
class SubmitJobForm:
    def __init__(self):
        self.strJobManagerID = None
        self.mapAppJobInfo = MapAppJobInfo()


# 提交作业详细参数封装类
class MapAppJobInfo:
    def __init__(self):
        self.GAP_WORK_DIR = None
        self.GAP_STD_ERR_FILE = None
        self.GAP_STD_OUT_FILE = None
        self.GAP_APPNAME = None
        self.GAP_WALL_TIME = None
        self.GAP_NPROC = None
        self.GAP_QUEUE = None
        self.GAP_NNODE = None
        self.GAP_SUBMIT_TYPE = None
        self.GAP_NDCU = None
        self.GAP_NGPU = None
        self.GAP_CMD_FILE = None
        self.GAP_JOB_NAME = None


# 提交作业参数封装json
class SubmitJobFormEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SubmitJobForm):
            return {
                'strJobManagerID': obj.strJobManagerID,
                'mapAppJobInfo': obj.mapAppJobInfo.__dict__
            }
        return super().default(obj)


# =====================以下为曙光接口======================================
# 获取曙光令牌方法
def get_tokens(user, password):
    # 参数校验
    if not user:
        raise ValueError("Invalid user")
    if not password:
        raise ValueError("Invalid password")
    url = "https://ac.sugon.com/ac/openapi/v2/tokens"
    headers = {
        'user': user,
        'password': password,
        'orgId': "4af12268f09383b061bb3c9f0c2d75e9"
    }
    try:
        response = HttpUtil.post(url, headers=headers)
        response_data = json.loads(response.text)
        if response_data['code'] == "0":
            data_list = response_data['data']
            for data in data_list:
                if data['clusterId'] == "11250":
                    token = data['token']
                    return token
        else:
            raise ValueError("Failed to fetch tokens")
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 获取授权区域地址
def get_enable_url(token, url_type):
    """
      url_type参数
          efileUrls   获取 文件传输 相关授权区域地址
          hpcUrls     获取 作业管理相 关授权区域地址
          aiUrls      获取 容器服务 相关授权区域地址
          eshellUrls  获取 ESHELL服务 相关授权区域地址
    """
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not url_type:
        raise ValueError("Invalid url_type")
    if url_type not in ["efileUrls", "hpcUrls", "aiUrls", "eshellUrls"]:
        raise ValueError("Invalid url_type")

    url = "https://ac.sugon.com/ac/openapi/v2/center"
    headers = {'token': token}

    try:
        response = HttpUtil.get(url, headers=headers)
        response_data = json.loads(response.text)
        if response_data['code'] == "0":
            data_urls = response_data['data']
            enable_urls = data_urls.get(url_type, [])
            for enable_url in enable_urls:
                if enable_url['enable'] == "true":
                    return enable_url['url']
            print("No available authorization region")
        else:
            raise ValueError("Failed to fetch enable urls")
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查询提交作业区域信息 调度器ID
def get_job_cluster(token, hpc_prefix):
    # 参数校验
    if not hpc_prefix:
        raise ValueError("Invalid hpc_prefix")
    if not token:
        raise ValueError("Invalid token")
    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/cluster"
    headers = {
        "token": token
    }

    try:
        response = HttpUtil.get(url, headers=headers)
        print(response.text)
        response.raise_for_status()
        response_data = json.loads(response.text)
        if response_data['code'] == "0":
            data_list = response_data['data']
            for data in data_list:
                job_cluster = data['id']
                return job_cluster
        else:
            raise ValueError("Failed to fetch job_cluster")
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查询提交作业队列资源信息 队列ID
def get_job_queues(token, hpc_prefix, user, job_cluster):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid hpc_prefix")
    if not user:
        raise ValueError("Invalid user")
    if not job_cluster:
        raise ValueError("Invalid job_cluster")
    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/queuenames/users/" + user
    headers = {
        "token": token
    }
    params = {
        "strJobManagerID": job_cluster
    }
    try:
        response = HttpUtil.get(url, headers=headers, params=params)
        response.raise_for_status()
        print(response.text)
        response_data = json.loads(response.text)
        if response_data['code'] == "0":
            data_list = response_data['data']
            for data in data_list:
                #  kshcnormal cpu共享型队列
                #  kshdexclu17 dpu独占型队列
                #  kshdnormal dpu共享型队列
                if data['queueName'] == "kshcnormal":
                    job_queues = data['id']
                    return job_queues
        else:
            raise ValueError("Failed to fetch job_cluster")
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 提交作业
def submit_job(token, hpc_prefix, cluster, queue, job_cmd, job_name, job_work_dir):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")

    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/apptemplates/BASIC/BASE/job"
    submitJobForm = SubmitJobForm()
    submitJobForm.strJobManagerID = int(cluster)  # 通过getCluster接口去获取调度器ID
    jobInfo = MapAppJobInfo()
    jobInfo.GAP_WORK_DIR = "/work/home/acsx6nwsm6" if job_work_dir == '' else job_work_dir
    jobInfo.GAP_STD_ERR_FILE = "/work/home/acsx6nwsm6" + "/std.err.%j" if job_work_dir == '' else job_work_dir + "/std.err.%j"
    jobInfo.GAP_STD_OUT_FILE = "/work/home/acsx6nwsm6" + "/std.out.%j" if job_work_dir == '' else job_work_dir + "/std.out.%j"
    jobInfo.GAP_APPNAME = "BASE"
    jobInfo.GAP_WALL_TIME = "24:00:00"
    jobInfo.GAP_NPROC = "1"
    jobInfo.GAP_QUEUE = queue
    jobInfo.GAP_NNODE = "1"
    jobInfo.GAP_SUBMIT_TYPE = "cmd"
    jobInfo.GAP_NDCU = ""
    jobInfo.GAP_NGPU = ""
    jobInfo.GAP_CMD_FILE = job_cmd
    jobInfo.GAP_JOB_NAME = job_name

    submitJobForm.mapAppJobInfo = jobInfo
    headers = {
        'token': token,
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.15.2",
        'Accept': "*/*",
        'Host': "ai111.hpccube.com:65061",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "543",
        'Connection': "keep-alive"
    }
    json_str = json.dumps(submitJobForm, cls=SubmitJobFormEncoder)
    print(json_str)
    try:
        response = HttpUtil.post(url, headers=headers, data=json_str)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查看文件
def view_files(token, hpc_prefix, dir_path):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid hpc_prefix")
    if not dir_path:
        raise ValueError("Invalid dir_path")
    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/file/content"
    getContent_map = {
        "hostName": "",
        "dirPath": dir_path,
        "triggerNum": 1,
        "rollDirection": "UP"
    }

    headers = {
        "token": token
    }

    try:
        response = HttpUtil.post(url, headers=headers, data=getContent_map)
        response.raise_for_status()
        print("___文件查看结果输出: " + response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查询当前作业列表
def view_current_job_list(token, hpc_prefix, job_cluster, job_queues=None, user_name=None, job_id=None,
                          job_name=None, start=None, limit=None, job_stat=None):
    """
    token : token 必填
    hpc_prefix : 作业授权地址 必填
    job_cluster : 作业调度器ID 必填
    job_queues : 作业队列名称
    user_name : 用户名
    job_id : 作业ID
    job_name : 作业名称
    start : 起始坐标  0
    limit : 请求一次获取数据的数目  25
    job_stat : 作业运行状态  # 'statR(运行)','statQ(排队)','statH(保留)','statS(挂起)','statE(退出)','statC(完成)','statW(等待)','statX(其他)'
    """
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid hpc_prefix")
    if not job_cluster:
        raise ValueError("Invalid job_cluster")
    if not start:
        start = 0
    if not limit:
        limit = 25
    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/jobs"
    params = {
        "strClusterIDList": job_cluster,  # 调度器ID  必填
        "strJobOwner": user_name,  # 用户名
        "strJobName": job_name,  # 作业名称
        "strJobId": job_id,  # 作业ID
        "start": start,  # 起始坐标
        "limit": limit,  # 请求一次获取数据的数目
        "strQueueName": job_queues,  # 队列名称
        "strJobStat": job_stat,  # 作业运行状态
    }
    headers = {
        "token": token
    }

    try:
        response = HttpUtil.get(url, headers=headers, params=params)
        print(response)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查询历史作业列表
def view_history_job_list(token, hpc_prefix, job_cluster, start_time, end_time, job_queues=None, user_name=None,
                          job_id=None, job_name=None, start=None, limit=None, job_stat=None, time_type=None,
                          app_type=None, sort=None, order_by=None, host_name=None, is_query_by_queue_time=None):
    """
     token : token 必填
     hpc_prefix : 作业授权地址 必填
     job_cluster : 作业调度器ID 必填
     start_time : 开始时间 必填  2023-08-15 00:00:00
     end_time : 结束时间 必填  2023-08-21 23:59:59
     job_queues : 作业队列名称
     user_name : 用户名
     job_id : 作业ID
     job_name : 作业名称
     start : 起始坐标  0
     limit : 请求一次获取数据的数目  25
     job_stat : 作业运行状态  # 'statR(运行)','statQ(排队)','statH(保留)','statS(挂起)','statE(退出)','statC(完成)','statW(等待)','statX(其他)'
     time_type : CUSTOM
     app_type : 应用名称
     sort : 排序规则   DESC/ASC
     order_by : 排序字段 	如：jobId
     host_name : 节点名称
     is_query_by_queue_time : 按照结束时间查询false/按照入队时间查询true（推荐false）
     """
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid hpc_prefix")
    if not job_cluster:
        raise ValueError("Invalid job_cluster")
    if not start_time:
        raise ValueError("Invalid start_time")
    if not end_time:
        raise ValueError("Invalid end_time")
    if not start:
        start = 0
    if not limit:
        limit = 25
    if not time_type:
        time_type = "CUSTOM"
    if not is_query_by_queue_time:
        is_query_by_queue_time = "false"
    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/historyjobs"
    params = {
        "strClusterNameList": job_cluster,  # 调度器ID
        "startTime": start_time,  # 开始时间 2021-11-23 01:01:01
        "endTime": end_time,  # 结束时间 2021-11-23 01:01:01
        "timeType": time_type,  # CUSTOM
        "queue": job_queues,  # 队列名称  非必填
        "appType": app_type,  # 应用名称  非必填
        "sort": sort,  # 排序规则  非必填
        "orderBy": order_by,  # 排序字段  非必填
        "jobId": job_id,  # 作业ID  非必填
        "jobState": job_stat,  # 运行状态  非必填
        # 'statR(运行)','statQ(排队)','statH(保留)','statS(挂起)','statE(退出)','statC(完成)','statW(等待)','statX(其他)'
        "hostName": host_name,  # 节点名称  非必填
        "strUser": user_name,  # 用户名称  非必填
        "jobName": job_name,  # 作业名称  非必填
        "start": start,  # 起始坐标
        "limit": limit,  # 请求一次获取数据的数目
        "isQueryByQueueTime": is_query_by_queue_time,  # 按照结束时间查询false/按照入队时间查询true（推荐false）
    }
    headers = {
        "token": token
    }

    try:
        response = HttpUtil.get(url, headers=headers, params=params)
        print(response)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查询作业详细信息(只能查当前作业列表)
def search_current_job_detail(token, hpc_prefix, job_id):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid efile_prefix")
    if not job_id:
        raise ValueError("Invalid job_id")

    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/jobs/" + job_id
    headers = {
        "token": token
    }

    try:
        response = HttpUtil.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 查询历史作业详细信息(只能查历史作业列表)
def search_history_job_detail(token, hpc_prefix, job_id, jobmanager_id, acct_time=None):
    """
    job_id : 作业ID
    jobmanager_id : 调度器ID
    acct_time : 入账时间（结束时间），建议传入，能够提升查询性能
    """
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid efile_prefix")
    if not job_id:
        raise ValueError("Invalid job_id")
    if not jobmanager_id:
        raise ValueError("Invalid jobmanager_id")
    if not acct_time:
        acct_time=""

    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/historyjobs/" + jobmanager_id + "/" + job_id + "?acctTime=" + acct_time
    headers = {
        "token": token
    }

    try:
        response = HttpUtil.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 删除作业(可批量)
def delete_job(token, hpc_prefix, job_info_map):
    """
    job_info_map : 待删除的作业信息，格式为调度器ID,用户名:作业号:; 如：1638523853,test:197:;1638523853,test:196:
    """
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not hpc_prefix:
        raise ValueError("Invalid hpc_prefix")
    if not job_info_map:
        raise ValueError("Invalid job_info_map")
    # 参数封装
    url = hpc_prefix + "/hpc/openapi/v2/jobs"
    params = {
        "jobMethod": "5",  # 作业操作类型，删除类型为5
        "strJobInfoMap": job_info_map
    }
    headers = {
        "token": token
    }

    try:
        response = HttpUtil.delete(url, headers=headers, params=params)
        print(response)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 获取文件
def search_files(token, efile_prefix, limit, start, key_word, path):
    # 参数校验
    if not efile_prefix:
        raise ValueError("Invalid efile_prefix")
    if not token:
        raise ValueError("Invalid token")
    # 参数封装
    url = efile_prefix + "/openapi/v2/file/list"
    params = {
        "limit": limit,
        "order": "desc",
        "orderBy": "lastModifiedTime",
        "path": path,
        "start": start,
        "keyWord": key_word
    }

    headers = {
        "token": token
    }

    try:
        response = HttpUtil.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 创建文件夹/文件
def mkdir(token, efile_prefix, path, create_parents):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not efile_prefix:
        raise ValueError("Invalid efile_prefix")
    if not path:
        raise ValueError("Invalid path")
    if not create_parents:
        create_parents = "false"

    # 参数封装
    # path, # 文件绝对路径
    # createParents  # 父目录不存在时是否创建，非必选，可选值：true:是；false:否,默认false
    url = efile_prefix + "/openapi/v2/file/mkdir?" + "path=" + path + "&createParents=" + create_parents
    headers = {
        "token": token
    }
    try:
        response = HttpUtil.post(url, headers=headers)
        response.raise_for_status()
        print("___创建目录结果: " + response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 文件上传
def upload_file(token, efile_prefix, path, cover, file):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not efile_prefix:
        raise ValueError("Invalid efile_prefix")
    if not path:
        raise ValueError("Invalid path")
    if not cover:
        cover = "uncover"
    if not file:
        raise ValueError("Invalid file")
    # 参数封装
    url = efile_prefix + "/openapi/v2/file/upload"
    files = {'file': open(file, 'rb')}
    print(files)
    upload_map = {
        # 文件路径
        "path": path,
        # cover:强制覆盖，uncover:不覆盖，默认：uncover
        "cover": cover,
    }
    headers = {
        "token": token
    }
    try:
        response = HttpUtil.post(url, headers=headers, data=upload_map, file=files)
        print(response)
        response.raise_for_status()
        print("upload_file: " + response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 判断文件/文件夹是否存在
def exist_file(token, efile_prefix, path):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not efile_prefix:
        raise ValueError("Invalid efile_prefix")
    if not path:
        raise ValueError("Invalid path")
    # 参数封装
    url = efile_prefix + "/openapi/v2/file/exist"
    exist_map = {
        # 文件/文件夹路径
        "path": path
    }
    headers = {
        "token": token
    }
    try:
        response = HttpUtil.post(url, headers=headers, data=exist_map)
        print(response)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e


# 文件/文件夹删除
def remove_file(token, efile_prefix, path, recursive):
    # 参数校验
    if not token:
        raise ValueError("Invalid token")
    if not efile_prefix:
        raise ValueError("Invalid efile_prefix")
    if not path:
        raise ValueError("Invalid path")
    if not recursive:
        recursive = "false"
    # 参数封装
    # 是否递归删除，非必选，可选值：true:是；false:否，默认false
    url = efile_prefix + "/openapi/v2/file/remove?" + "paths=" + path + "&recursive=" + recursive
    headers = {
        "token": token
    }
    try:
        response = HttpUtil.post(url, headers=headers)
        print(response)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to make a request to the server") from e
