import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText

from thonny.utils.SugonUtils import upload_file, get_enable_url, get_tokens, mkdir, search_files, view_files


class FileManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("曙光云文件管理")
        self.geometry("800x600")
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.TOP)

        self.back_button = tk.Button(self.button_frame, text="后退", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, anchor=tk.W)

        self.new_button = tk.Button(self.button_frame, text="新建目录", command=self.create_file)
        self.new_button.pack(side=tk.LEFT, padx=5)

        self.upload_button = tk.Button(self.button_frame, text="上传", command=self.upload_file)
        self.upload_button.pack(side=tk.LEFT, padx=5)

        self.upload_button = tk.Button(self.button_frame, text="刷新", command=self.refresh_list)
        self.upload_button.pack(side=tk.LEFT, padx=5)

        self.file_tree = ttk.Treeview(self)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.file_info_frame = tk.Frame(self)
        self.file_info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.file_info_label = tk.Label(self.file_info_frame, text="文件信息：")
        self.file_info_label.pack()

        self.open_button = tk.Button(self.file_info_frame, text="打开", command=self.open_file)
        self.open_button.configure(state=tk.DISABLED)
        self.open_button.pack()

        self.folder_close_icon = tk.PhotoImage(file="../res/closed-folder.gif")
        self.data = None
        self.default_text = None
        self.file_name = None
        self.current_path = None
        self.parent_path = None
        self.load_files()

    def load_files(self, folder_path=None):
        print(folder_path)
        self.file_tree.delete(*self.file_tree.get_children())
        token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
        enable_url = get_enable_url(token, "efileUrls")
        search_file = search_files(token, enable_url, 10, 0, None, folder_path)
        self.data = json.loads(search_file)
        self.current_path = self.data["data"]["path"]
        file_list = self.data["data"]["fileList"]
        children_list = self.data["data"]["children"]

        for child in children_list:
            self.file_tree.insert("", tk.END, text=f" {child['label']}", values=child,
                                  image=self.folder_close_icon)
        for file in file_list:
            self.file_tree.insert("", tk.END, text=file["name"], values=file)

        self.file_tree.bind("<<TreeviewSelect>>", self.show_file_info)

    def show_file_info(self, event):
        selected_item = self.file_tree.focus()
        print(selected_item)
        file_info_text = ""
        file = self.file_tree.item(selected_item)
        print(file)
        if file['image']:
            if file['image'][0].startswith("pyimage1"):
                path = file['values'][0].split("'path': ")[1].split(",")[0].strip("'")  # 使用字符串分割提取路径,去除路径中的引号
                file_info_text += f"文件夹名: {file['text']}\n"
                file_info_text += f"文件路径: {path}\n"
                self.open_button.configure(state=tk.NORMAL)
        else:
            file_info_text += f"文件夹名: {file['text']}\n"
            path = file['values'][0].split("'path': ")[1].split(",")[0].strip("'")  # 使用字符串分割提取路径,去除路径中的引号
            file_info_text += f"文件路径: {path}\n"
            owner = file['values'][0].split("'owner': ")[1].split(",")[0].strip("'")
            file_info_text += f"创建者: {owner}\n"
            size = file['values'][0].split("'size': ")[1].split(",")[0].strip("'")
            file_info_text += f"文件大小: {size} bytes\n"
            lastModifiedTime = file['values'][0].split("'lastModifiedTime': ")[1].split(",")[0].strip("'")
            file_info_text += f"最后修改时间: {lastModifiedTime}"
            print(file['values'])
            self.open_button.configure(state=tk.NORMAL)
            # self.open_button.configure(state=tk.DISABLED)

        self.file_info_label.configure(text=file_info_text)

    def open_file(self):
        selected_item = self.file_tree.focus()
        file = self.file_tree.item(selected_item)
        path = file['values'][0].split("'path': ")[1].split(",")[0].strip("'")
        if file['image']:
            print(f"打开文件夹路径: {path}")
            self.parent_path = self.current_path
            self.load_files(folder_path=path)
        else:
            print(f"打开文件路径: {path}")
            token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
            enable_url = get_enable_url(token, "hpcUrls")
            file_content = view_files(token, enable_url, path)
            file_content_o = json.loads(file_content)
            print(file_content_o)
            if file_content_o['code'] == "0":
                if file_content_o['data']['success'] == "true":
                    self.file_name = file['text']
                    self.default_text = file_content_o['data']['data']
                    print(f"文本内容: {self.default_text}")
                    editor_window = tk.Toplevel(self)
                    text_area = ScrolledText(editor_window, wrap=tk.WORD)
                    text_area.insert("1.0", self.default_text)
                    text_area.pack(fill=tk.BOTH, expand=True)

                    def save_on_ctrl_s():
                        text_content = text_area.get("1.0", tk.END)
                        print(text_content)
                        try:
                            with open(self.file_name, "w") as f:
                                f.write(text_content)
                            efile_url = get_enable_url(token, "efileUrls")
                            print(os.path.dirname(path))
                            upload_file(token, efile_url, os.path.dirname(path), "cover", self.file_name)
                            self.default_text = text_content
                            tk.messagebox.showinfo("保存成功", "文本保存成功。")
                        except Exception as e:
                            tk.messagebox.showerror("保存失败", f"保存文本时出错: {str(e)}")

                        # 使用完毕后删除临时文件
                        try:
                            os.remove(self.file_name)
                        except Exception as e:
                            print(f"Failed to delete the temporary file: {str(e)}")

                    editor_window.bind('<Control-s>', save_on_ctrl_s)

                    save_button = tk.Button(editor_window, text="保存", command=save_on_ctrl_s)
                    save_button.pack()

                    def on_close():
                        current_text = text_area.get("1.0", tk.END).strip()
                        if current_text != self.default_text:
                            result = messagebox.askyesnocancel("关闭文本", "是否要在关闭前保存更改？")
                            if result is True:
                                save_on_ctrl_s()
                                editor_window.destroy()
                            elif result is False:
                                editor_window.destroy()
                        else:
                            editor_window.destroy()

                    editor_window.protocol("WM_DELETE_WINDOW", on_close)
                else:
                    # 显示提示信息
                    self.open_button.configure(state=tk.DISABLED)
                    messagebox.showinfo("提示", f"目前仅支持文本文件打开查看")

            else:
                # 显示提示信息
                messagebox.showinfo("提示", f"远程连接失败")

    def go_back(self):
        # 执行返回操作
        # 调用接口或编写逻辑以实现后退功能
        print("Go Back")
        self.load_files(folder_path=self.parent_path)

    def create_file(self):
        # 执行新建文件操作
        # 调用接口或编写逻辑以实现新建文件功能
        print("Create File")
        file_name = simpledialog.askstring("新建目录", "请输入文件名")
        if file_name:
            # 调用接口或编写逻辑以实现创建文件功能
            print(f"Creating File: {file_name}")
            print(f"current_path: {self.current_path}")
            token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
            enable_url = get_enable_url(token, "efileUrls")
            mkdir(token, enable_url, self.current_path + "/" + file_name, "false")
            # 显示提示信息
            messagebox.showinfo("提示", f"创建文件 {file_name} 完成")

    def refresh_list(self):
        # 执行刷新文件列表操作
        # 调用接口或编写逻辑以实现新建文件功能
        print("Refresh List")
        self.load_files(folder_path=self.current_path)

    def upload_file(self):
        # 执行上传文件操作
        # 调用接口或编写逻辑以实现上传文件功能
        print("Upload File")
        file_path = filedialog.askopenfilename()
        if file_path:
            # 调用接口或编写逻辑以实现上传文件功能
            print(f"Uploading File: {file_path}")
            token = get_tokens("acsx6nwsm6", "yubo@liuzhongxiu")
            enable_url = get_enable_url(token, "efileUrls")
            upload_file(token, enable_url, self.current_path, "uncover", file_path)


app = FileManagerApp()
app.mainloop()
