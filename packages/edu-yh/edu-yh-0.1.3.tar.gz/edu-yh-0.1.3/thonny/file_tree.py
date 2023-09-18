import tkinter as tk
from tkinter import ttk

"""
这是树形demo
这是树形demo
这是树形demo
这是树形demo
这是树形demo
这是树形demo
这是树形demo
这是树形demo
这是树形demo
这是树形demo
"""


class FileTree:
    def __init__(self, root):
        self.root = root
        self.tree = None

    def create_tree(self):
        # 创建 Treeview
        self.tree = ttk.Treeview(self.root)

        # 添加根节点
        self.tree.insert("", "end", text="根目录", open=True)

        # 添加子节点
        folder1 = self.tree.insert("", "end", text="文件夹1", open=True)
        file11 = self.tree.insert(folder1, "end", text="文件1-1")
        file12 = self.tree.insert(folder1, "end", text="文件1-2")

        folder2 = self.tree.insert("", "end", text="文件夹2", open=True)
        file21 = self.tree.insert(folder2, "end", text="文件2-1")
        file22 = self.tree.insert(folder2, "end", text="文件2-2")

        # 绑定点击事件
        self.tree.bind("<Double-Button-1>", self.toggle_tree)

        # 设置样式
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12))

        # 显示 Treeview
        self.tree.pack(expand=True, fill="both")

    def toggle_tree(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            res = self.tree.item(item_id, open=not self.tree.item(item_id, "open"))
            print(res)


# 创建根窗口和 FileTree 对象
root = tk.Tk()
root.title("可折叠文件树")
file_tree = FileTree(root)

# 创建文件树
file_tree.create_tree()

# root.mainloop()
