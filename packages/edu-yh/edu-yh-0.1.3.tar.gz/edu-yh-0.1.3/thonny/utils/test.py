from thonny.utils.SugonUtils import get_tokens, get_enable_url, mkdir

# 1、获取令牌的方法
token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
print(token)
# 2、获取对应操作授权地址 efileUrls hpcUrls eshellUrls
enable_url = get_enable_url(token, "efileUrls")
print(enable_url)
# 文件列表，文件搜索
# search_file = search_files(token, enable_url, 10, 0, None, None)
# print(search_file)
# # 3、作业集群获取
# job_cluster = get_job_cluster(token, enable_url)
# print(job_cluster)
# # 4、作业队列获取
# job_queues = get_job_queues(token, enable_url, "acsx6nwsm6", job_cluster)
# print(job_queues)
# # 5、提交作业
# submit_job = submit_job(token, enable_url, job_cluster, job_queues, "ls", "007", "")
# print(submit_job)
# 6、查看文件
# file_content = view_files(token, enable_url, "/public/home/acsx6nwsm6/test.py")
# print(file_content)
# 7、文件创建
mkdir_info = mkdir(token, enable_url, "/public/home/acsx6nwsm6/test20230821.txt", "false")
print(mkdir_info)
# 8、文件上传
# upload_info = upload_file(token, enable_url, "/public/home/acsx6nwsm6/test20230821/", "uncover", "D:/AFoooooo/ai1.jpg")
# print(upload_info)
# 9、判断文件/文件夹是否存在
# exist_info = exist_file(token, enable_url, "/public/home/acsx6nwsm6/test20230821/")
# print(exist_info)
# 10、删除文件/文件夹是否存在
# remove_info = remove_file(token, enable_url, "/public/home/acsx6nwsm6/test20230821/ai1.jpg", "false")
# print(remove_info)
# 11、查询当前作业列表
# current_job_list = view_current_job_list(token=token, hpc_prefix=enable_url, job_cluster=job_cluster)
# print(current_job_list)
# 12、查询历史作业列表
# history_job_list = view_history_job_list(token=token, hpc_prefix=enable_url, job_cluster=job_cluster,
#                                          start_time="2023-08-15 00:00:00",
#                                          end_time="2023-08-21 23:59:59")
# print(history_job_list)
# 13、删除作业
# delete_job_info = delete_job(token, enable_url, "1573088268,acsx6nwsm6:40615631:")
# print(delete_job_info)
# 14、查询作业详细信息(只能查当前作业列表)
# current_job_detail = search_current_job_detail(token, enable_url, "40618124")
# print(current_job_detail)
# 15、查询历史作业详细信息(只能查历史作业列表)
# job_detail = search_history_job_detail(token=token, hpc_prefix=enable_url, job_id="40618124",
#                                        jobmanager_id="1573088268")#  不传入账时间（结束时间），查询巨慢
# job_detail = search_history_job_detail(token=token, hpc_prefix=enable_url, job_id="40618124",
#                                        jobmanager_id="1573088268", acct_time="2023-08-21 11:50:34")
# history_job_detail = search_history_job_detail(token, enable_url, "40618124", "1573088268", "2023-08-21 11:50:34")
# history_job_detail = search_history_job_detail(token, enable_url, "40615631", "1573088268", "2023-08-21 10:24:12")
# print(history_job_detail)




# from PIL import Image
#
# # 打开原始图片
# image = Image.open('../thonny/res/ac.png')
#
# # 将图片调整为16x16大小
# resized_image = image.resize((16, 16), Image.ANTIALIAS)
#
# # 保存调整后的图片
# resized_image.save('../thonny/res/ac_16x16.png')
