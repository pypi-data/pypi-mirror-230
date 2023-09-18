import json
import threading
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from thonny.utils.SugonUtils import (
    get_enable_url,
    get_job_cluster,
    get_job_queues,
    get_tokens,
    search_history_job_detail,
    submit_job,
    view_current_job_list,
    view_history_job_list,
)

from thonny import get_workbench
from thonny.time_select import DateTimePicker
from thonny.ui_utils import (
    CommonDialog,
)

import time

class WorkDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master=master)
        self.title("曙光作业")
        screen_width = self.winfo_screenwidth()
        self.center_window(screen_width - 100, 600)
        self.token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
        self.enable_url = get_enable_url(self.token, "hpcUrls")
        self.job_cluster = get_job_cluster(self.token, self.enable_url)

        # 创建选项卡控件
        self.tabControl = ttk.Notebook(self)
        self.tabControl.pack(fill="both", expand=1)

        # 创建选项卡1
        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text="当前作业")

        # 在选项卡1中添加表格
        columns = ["作业id", "作业名", "应用", "队列", "区域", "开始时间", "运行时长", "状态"]
        self.treeview1 = ttk.Treeview(self.tab1, columns=columns, show="headings")
        for col in columns:
            self.treeview1.heading(col, text=col)
            self.treeview1.column(col, anchor="center")  # 设置列内容居中对齐
        self.treeview1.pack(padx=20, pady=20)

        # 创建按钮
        add_button = tk.Button(self.tab1, text="新增", command=self.add_data)
        add_button.pack(side=tk.LEFT, padx=10)
        delete_button = tk.Button(self.tab1, text="删除", command=self.delete_data)
        delete_button.pack(side=tk.LEFT, padx=10)

        # 创建选项卡2
        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text="历史作业")

        delete_button1 = tk.Button(self.tab2, text="查看详情", command=self.look_data)
        delete_button1.pack(side=tk.BOTTOM, pady=50)

        self.headerDiv = tk.Frame(self.tab2)
        self.headerDiv.pack(side=tk.TOP, pady=20, padx=10, anchor="w")

        self.statString = tk.StringVar()
        self.endString = tk.StringVar()
        self.statString.set(self.get_previous_year(30))
        self.endString.set(self.get_previous_year(0))

        start_btn = tk.Button(self.headerDiv, text="选择开始时间", command=self.select_start)
        start_btn.grid(row=0, column=1, padx=30)

        start_lab = tk.Label(self.headerDiv, textvariable=self.statString)
        start_lab.grid(row=1, column=1)

        start_btn = tk.Button(self.headerDiv, text="选择结束时间", command=self.select_end)
        start_btn.grid(row=0, column=2, padx=30)

        end_lab = tk.Label(self.headerDiv, textvariable=self.endString)
        end_lab.grid(row=1, column=2)

        select_btn = tk.Button(self.headerDiv, text="查询", command=self.select_click)
        select_btn.grid(row=0, column=4, padx=30)

        # 在选项卡2中添加空表格

        columnsHis = ["作业id", "作业名", "应用", "队列", "区域", "结束时间", "运行时长", "状态"]
        self.treeview2 = ttk.Treeview(self.tab2, columns=columnsHis, show="headings")
        for col in columnsHis:
            self.treeview2.heading(col, text=col)
            self.treeview2.column(col, anchor="center")  # 设置列内容居中对齐
        self.treeview2.pack(padx=80, pady=80)

        # 绑定选项卡切换事件
        self.tabControl.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 初始化数据
        self.data1 = []
        self.data2 = []
        current_job_list = view_current_job_list(
            token=self.token, hpc_prefix=self.enable_url, job_cluster=self.job_cluster
        )
        reqResult = json.loads(current_job_list)["data"]["list"]
        if reqResult is None:
            reqResult = []
        self.soureData2 = reqResult
        for item in reqResult:
            temp = []
            temp.append(item["jobId"])
            temp.append(item["jobName"])
            temp.append(item["appType"])
            temp.append(item["queue"])
            temp.append(item["jobmanagerName"])
            temp.append(item["jobStartTime"])
            temp.append(item["jobRunTime"])
            temp.append(self.checkStatus(item["jobStatus"]))
            self.data1.append(temp)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        ten_days_later = current_time + timedelta(days=10)
        next_time = ten_days_later.strftime("%Y-%m-%d %H:%M:%S")

        history_job_list = view_history_job_list(
            token=self.token,
            hpc_prefix=self.enable_url,
            job_cluster=self.job_cluster,
            start_time=formatted_time,
            end_time=next_time,
        )
        reqResult = json.loads(history_job_list)["data"]["list"]
        if reqResult is None:
            reqResult = []
        self.soureData = reqResult
        for item in reqResult:
            temp = []
            temp.append(item["jobmanagerId"])
            temp.append(item["jobName"])
            temp.append(item["appType"])
            temp.append(item["queue"])
            temp.append("嘿嘿区域")
            temp.append(item["jobEndTime"])
            temp.append(item["jobWalltimeUsed"])
            temp.append(self.checkStatus(item["jobState"]))
            self.data2.append(temp)

        self.load_data(self.treeview1, self.data1)  # 初始化选项卡1的数据

    def select_start(self):
        self.float_div = tk.Toplevel(self.headerDiv)
        # 设置为模态
        self.float_div.grab_set()
        # 设置宽高
        self.float_div.geometry("600x600")
        self.float_div.title("开始时间:")
        res = DateTimePicker(self.float_div, "开始时间")
        # 添加获取选定时间的操作
        get_time_button = ttk.Button(
            self.float_div, text="确定", command=lambda: self.get_selected_time(res)
        )
        get_time_button.pack(pady=10)

    def select_end(self):
        self.float_div = tk.Toplevel(self.headerDiv)
        # 设置为模态
        self.float_div.grab_set()
        # 设置宽高
        self.float_div.geometry("600x600")
        self.float_div.title("结束时间:")
        res = DateTimePicker(self.float_div, "结束时间")
        # 添加获取选定时间的操作
        get_time_button = ttk.Button(
            self.float_div, text="确定", command=lambda: self.get_selected_time_end(res)
        )
        get_time_button.pack(pady=10)

    def get_selected_time(self, datetime_picker):
        selected_time = datetime_picker.get_selected_datetime()
        # 在这里进行您想要的操作，使用选定的时间 'selected_time'
        self.statString.set(selected_time)
        self.float_div.destroy()

    def get_selected_time_end(self, datetime_picker):
        selected_time = datetime_picker.get_selected_datetime()
        # 在这里进行您想要的操作，使用选定的时间 'selected_time'
        self.endString.set(selected_time)
        self.float_div.destroy()

    def get_previous_year(self, day):
        # 获取当前时间
        current_time = datetime.now()

        # 计算并返回当前时间减一年后的结果
        previous_year = current_time - timedelta(days=day)
        previous_year_str = previous_year.strftime('%Y-%m-%d %H:%M:%S')
        return previous_year_str

    def select_click(self):
        start = self.statString.get()
        end = self.endString.get()

        def request_api():
            nonlocal history_job_list  # 使用nonlocal关键字声明history_job_list为外部变量，以便在函数内部对其进行赋值
            history_job_list = view_history_job_list(
                token=self.token,
                hpc_prefix=self.enable_url,
                job_cluster=self.job_cluster,
                start_time=start,
                end_time=end,
            )
            # 创建一个新线程执行接口请求

        t = threading.Thread(target=request_api)
        t.start()

        t.join(timeout=30)
        if t.is_alive():
            messagebox.showerror('错误', '曙光服务器繁忙，请在空闲时间重试')
            return
        # 获取接口请求开始时间
        history_job_list = view_history_job_list(
            token=self.token,
            hpc_prefix=self.enable_url,
            job_cluster=self.job_cluster,
            start_time=start,
            end_time=end,
        )# 获取接口请求结束时间


        reqResult = json.loads(history_job_list)["data"]["list"]
        if reqResult is None:
            reqResult = []
        self.soureData = reqResult
        for item in reqResult:
            temp = []
            temp.append(item["jobmanagerId"])
            temp.append(item["jobName"])
            temp.append(item["appType"])
            temp.append(item["queue"])
            temp.append("嘿嘿区域")
            temp.append(item["jobEndTime"])
            temp.append(item["jobWalltimeUsed"])
            temp.append(self.checkStatus(item["jobState"]))
            self.data2.append(temp)
        self.load_data(self.treeview2, self.data2)

    def validate_datetime_format(self, input_datetime):
        try:
            datetime.strptime(input_datetime, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    def checkStatus(self, type):
        if type == "statR":
            return "运行"
        elif type == "statQ":
            return "排队"
        elif type == "statH":
            return "保留"
        elif type == "statS":
            return "挂起"
        elif type == "statE":
            return "退出"
        elif type == "statC":
            return "完成"
        elif type == "statW":
            return "等待"
        elif type == "statX":
            return "完成"

    def add_data(self):
        # 创建下拉选择框
        self.new_window = tk.Toplevel(master=self)
        self.new_window.grab_set()
        self.new_window.title("新窗口")
        label_submission = tk.Label(self.new_window, text="提交方式:")
        label_submission.pack()
        self.combo_submission = ttk.Combobox(self.new_window, values=["命令行方式"])
        self.combo_submission.pack()
        default_value = "命令行方式"
        self.combo_submission.current(self.combo_submission["values"].index(default_value))

        # 创建标签和输入框
        label_name = tk.Label(self.new_window, text="作业名称:")
        label_name.pack()
        self.entry_name = tk.Entry(self.new_window)
        self.entry_name.pack()

        # 创建选择文件目录按钮
        label_directory = tk.Label(self.new_window, text="工作目录:")
        label_directory.pack()
        self.entry_directory = tk.Entry(self.new_window)
        self.entry_directory.pack()
        # button_select_directory = tk.Button(self, text="选择文件目录", command=self.select_directory)
        # button_select_directory.pack()

        # 创建命令行方式的文本输入框
        label_command = tk.Label(self.new_window, text="命令行方式:")
        label_command.pack()
        self.text_command = tk.Text(self.new_window, height=10)
        self.text_command.pack()
        default_text = "sleep 5"
        self.text_command.insert("1.0", default_text)

        # 创建提交按钮
        button_submit = tk.Button(self.new_window, text="提交", command=self.submit_homework)
        button_submit.pack()

    def delete_data(self):
        # 获取选中行的索引
        selection = self.treeview1.selection()
        if selection:
            index = int(self.treeview1.index(selection[0]))
            # messagebox.showinfo('选择的下标', '你选择的下标是' + str(index))
            res_snow = self.soureData2[index]
            print("获取的结果", res_snow)
        else:
            messagebox.showerror("错误", "你啥也没选")

    def look_data(self):
        # 获取选中行的索引
        selection = self.treeview2.selection()
        if selection:
            index = int(self.treeview2.index(selection[0]))
            row = self.soureData[index]
            job_detail = search_history_job_detail(
                token=self.token,
                hpc_prefix=self.enable_url,
                job_id=str(row["jobId"]),
                jobmanager_id=str(row["jobmanagerId"]),
                acct_time=str(row["jobEndTime"]),
            )  # 不传入账时间（结束时间），查询巨慢
            resJson = json.loads(job_detail)
            print(666, resJson)
            data_dict = resJson["data"]
            self.new_window1 = tk.Toplevel(master=self)
            self.new_window1.grab_set()
            self.new_window1.title("新窗口")
            self.new_window1.geometry("500x500")
            # 创建滚动区域
            scrollbar = ttk.Scrollbar(self.new_window1)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            # 创建滚动文本框，并设置为不可编辑状态
            text_box = tk.Text(self.new_window1, yscrollcommand=scrollbar.set)

            text_box.pack(fill=tk.BOTH, expand=True)
            # 配置滚动条和滚动文本框的关联
            scrollbar.config(command=text_box.yview)
            # 将数据字典内容添加到滚动文本框中
            for key, value in data_dict.items():
                text_box.insert(tk.END, f"{self.checkStatusKey(key)}: {value}\n")
        else:
            messagebox.showerror("错误", "你啥也没选")

    def checkStatusKey(self, type):
        status_dict = {
            "acctTime": "记账时间",
            "appType": "应用类型",
            "command": "作业脚本的位置",
            "commandExist": "作业脚本是否存在",
            "cpuNuclearHour": "CPU核时",
            "cpuNuclearSec": "CPU核秒",
            "cpuUnitPrice": "作业提交时当时的CPU单价",
            "dcuCardHour": "DCU卡时",
            "dcuCardSec": "DCU卡秒",
            "dcuUnitPrice": "作业提交时当时的DCU单价",
            "efficiencyCpu": "CPU效率",
            "exclusiveCputime": "作业独占的cputime，单位为秒，当作业为独占作业时有值，否则为0",
            "exclusiveMem": "作业独占的mem",
            "exclusiveWalltime": "作业独占的walltime，单位为秒，当作业为独占作业时有值，否则为0",
            "goldenable": "作业提交时当时的计费状态",
            "gpuCardHour": "GPU卡时",
            "gpuCardSec": "GPU卡秒",
            "gpuUnitPrice": "作业提交时当时的GPU单价",
            "groupName": "用户组名",
            "historyAccount": "作业运行结束后当时作业提交者所属的账号",
            "historyQueuerate": "作业提交时当时的队列费率",
            "isSinglejob": "是否为独占节点的作业",
            "jobCpuTime": "作业占用的CPU时间",
            "jobDcuNum": "作业使用的DCU数",
            "jobEndTime": "作业结束时间",
            "jobExecGpus": "作业占用的Gpu节点",
            "jobExecHost": "作业执行节点",
            "jobExitStatus": "作业退出代码",
            "jobGpuNum": "作业使用的GPU核数",
            "jobId": "作业ID",
            "jobMemUsed": "作业使用的物理内存数，单位kb",
            "jobName": "作业名",
            "jobProcNum": "作业使用的处理器数(表示核数)",
            "jobQueueTime": "作业入队时间，对应记账属性qtime",
            "jobReqCpu": "申请CPU",
            "jobReqDcu": "申请DCU",
            "jobReqGpu": "申请GPU",
            "jobReqMem": "申请内存",
            "jobReqNodes": "申请节点数",
            "jobResponseTime": "作业响应时间JobEndTime-JobQueueTime,单位为秒",
            "jobStartTime": "作业启动时间",
            "jobState": "作业状态",
            "jobVmemUsed": "作业使用的虚拟内存，单位kb",
            "jobWaitTime": "作业等待时间JobStartTime-JobQueueTime,单位为秒",
            "jobWalltimeUsed": "作业实际使用的Walltime,单位为秒",
            "jobmanagerId": "区域ID",
            "jobmanagerName": "区域名称",
            "needNodes": "分配的节点名或节点数",
            "nodect": "分配的节点数",
            "owner": "作业拥有者",
            "queue": "队列",
            "scale": "作业的规模",
            "shareCputime": "作业共享的cputime，单位为秒，当作业为非独占作业时有值，否则为0",
            "shareMem": "作业共享的mem，单位kb，当作业为非独占作业时有值，否则为0",
            "shareWalltime": "作业共享的walltime，单位为秒，当作业为非独占作业时有值，否则为0",
            "isSinglejob": "是否为独立结点作业",
            "startCount": "作业的启动次数，在对应的数据库表中没有这个字段",
            "userName": "用户名",
            "walltime": "提交作业时请求的Walltime或系统默认的Walltime,单位为秒",
            "workdir": "作业的工作路径",
        }

        if type in status_dict:
            if type == "jobState":
                return self.checkStatus(status_dict[type])
            return status_dict[type]
        else:
            return "未知状态"

    def submit_homework(self):
        # 获取下拉选择框的值
        submission_method = self.combo_submission.get()

        # 获取文本输入框的值
        job_name = self.entry_name.get()
        working_directory = self.entry_directory.get()
        command_line = self.text_command.get("1.0", tk.END)

        if submission_method == "命令行方式":
            print("命令行:", command_line)
            if not command_line.strip():
                # command_line为空
                messagebox.showerror(
                    "提交作业",
                    "命令行脚本不能为空\n\n",
                    master=get_workbench(),
                )
            else:
                if command_line:
                    # 在这里可以将作业提交到服务器或进行其他处理
                    # todo 曙光账号来源
                    token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
                    enable_url = get_enable_url(token, "hpcUrls")
                    job_cluster = get_job_cluster(token, enable_url)
                    job_queues = get_job_queues(token, enable_url, "acsx6nwsm6", job_cluster)
                    job_info = submit_job(
                        token,
                        enable_url,
                        job_cluster,
                        job_queues,
                        command_line,
                        job_name,
                        working_directory,
                    )
                    print("提交请求:", job_info)
                    # 提交成功提示窗口
                    messagebox.showinfo("提交成功", "作业已成功提交！")
                    # 关闭弹出框
                    self.new_window.destroy()

                    current_job_list = view_current_job_list(
                        token=self.token, hpc_prefix=self.enable_url, job_cluster=self.job_cluster
                    )
                    reqResult = json.loads(current_job_list)["data"]["list"]
                    if reqResult is None:
                        reqResult = []
                    reqResult
                    for item in reqResult:
                        temp = []
                        temp.append(item["jobId"])
                        temp.append(item["jobName"])
                        temp.append(item["appType"])
                        temp.append(item["queue"])
                        temp.append(item["jobmanagerName"])
                        temp.append(item["jobStartTime"])
                        temp.append(item["jobRunTime"])
                        temp.append(self.checkStatus(item["jobStatus"]))
                        self.data1.append(temp)
                    self.load_data(self.treeview1, self.data1)

    def load_data(self, treeview, data):
        # 清除表格数据
        treeview.delete(*treeview.get_children())

        # 添加新数据
        for row in data:
            treeview.insert("", tk.END, values=row)

    def on_tab_changed(self, event):
        current_tab = event.widget.tab(event.widget.select(), "text")
        if current_tab == "当前作业":
            self.load_data(self.treeview1, self.data1)
        elif current_tab == "历史作业":
            self.load_data(self.treeview2, self.data2)

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
