import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


def submit_homework():
    # 获取下拉选择框的值
    submission_method = combo_submission.get()

    # 获取文本输入框的值
    homework_name = entry_name.get()
    working_directory = entry_directory.get()
    command_line = text_command.get("1.0", tk.END)

    # 打印提交的作业信息
    print("提交方式:", submission_method)
    print("作业名称:", homework_name)
    print("工作目录:", working_directory)

    if submission_method == "命令行方式":
        print("命令行:", command_line)

    # 在这里可以将作业提交到服务器或进行其他处理


def select_directory():
    # 弹出选择文件夹对话框
    directory = filedialog.askdirectory()
    # 将选择的文件夹路径显示在输入框中
    entry_directory.delete(0, tk.END)
    entry_directory.insert(tk.END, directory)


# 创建主窗口
window = tk.Tk()
window.title("提交作业")
window.geometry("400x600")

# 创建下拉选择框
label_submission = tk.Label(window, text="提交方式:")
label_submission.pack()
combo_submission = ttk.Combobox(window, values=["命令行方式", "Bash脚本方式", "调度脚本方式"])
combo_submission.pack()

# 创建标签和输入框
label_name = tk.Label(window, text="作业名称:")
label_name.pack()
entry_name = tk.Entry(window)
entry_name.pack()

# 创建选择文件目录按钮
label_directory = tk.Label(window, text="工作目录:")
label_directory.pack()
entry_directory = tk.Entry(window)
entry_directory.pack()
button_select_directory = tk.Button(window, text="选择文件目录", command=select_directory)
button_select_directory.pack()

# 创建命令行方式的文本输入框
label_command = tk.Label(window, text="命令行方式:")
label_command.pack()
text_command = tk.Text(window, height=10)
text_command.pack()

# 创建提交按钮
button_submit = tk.Button(window, text="提交", command=submit_homework)
button_submit.pack()

# 启动主循环
window.mainloop()
