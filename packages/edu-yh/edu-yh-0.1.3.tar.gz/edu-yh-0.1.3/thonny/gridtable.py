import math
import tkinter as tk
from tkinter import ttk

from thonny import get_workbench

"""
在初始化函数中，通过传入参数来设置表格的各种属性，如头部行数、数据行数、尾部行数和冻结列数等。还初始化了一些变量，如屏幕行高、可见的数据行数等，并调用了update_header_rows()函数来更新表格的头部行。

set_data()函数用于设置表格的数据，接受一个字典类型的参数data_rows，将其赋值给self.data_rows，并更新屏幕上显示的数据。

update_header_rows()函数用于更新表格的头部行。通过循环遍历头部行和列，获取并设置头部小部件的文本内容，并将其放置在指定的行列位置。

get_data_widget()和get_header_widget()函数用于获取数据和头部小部件。如果指定行列位置的小部件不存在，则通过调用create_data_widget()和create_header_widget()函数来创建一个新的小部件，并将其保存在相应的字典中，然后返回该小部件。

create_data_widget()和create_header_widget()函数分别用于创建数据和头部小部件，设置其背景色、文本对齐方式和内边距等样式。

set_first_visible_data_row_no()函数用于设置第一个可见的数据行号。它根据传入的行号n，计算最终的值，并调用update_screen_data()函数来更新屏幕上显示的数据。

_clear_screen_row()函数用于清除指定行号的所有小部件。

update_screen_widgets()函数用于更新屏幕上显示的小部件。它根据可用的屏幕高度计算最大可显示的行数，并根据表格的头部行数、数据行数和尾部行数等条件，确定最终的目标行数。然后根据目标行数和当前的屏幕行数，动态地添加或移除小部件。

update_screen_data()函数用于更新屏幕上显示的数据。首先调用update_screen_widgets()函数获取可用的屏幕高度，然后根据当前的可见数据行数和头部行数、数据行数，遍历并更新相应的小部件的文本内容。

get_data_value()和get_header_value()函数分别用于获取数据行和头部行中指定位置的值。

最后，on_configure()函数是一个事件处理函数，当窗口大小发生变化时自动调用。它获取新的窗口高度，并通过调用update_screen_widgets()函数来更新屏幕上的小部件和数据。
"""


class GridTable(tk.Frame):
    def __init__(self, master, header_rows, data_row_count, footer_row_count, frozen_column_count):
        super().__init__(master)

        self.header_widgets = {}
        self.data_widgets = {}

        self.bind("<Configure>", self.on_configure, True)

        self.screen_row_height = 22  # TODO:

        self.first_visible_data_row_no = 0
        self.visible_data_row_count = 0
        self.header_rows = header_rows
        self.data_rows = {}

        self.screen_row_count = 0
        self.data_row_count = data_row_count
        self.column_count = len(self.header_rows[-1])
        self.header_row_count = len(header_rows)
        self.footer_row_count = footer_row_count
        self.frozen_column_count = frozen_column_count

        self.update_header_rows()

    def set_data(self, data_rows):
        # self.data_rows.update(data_rows) # dict version
        self.data_rows = data_rows
        self.data_row_count = len(data_rows)
        self.update_screen_data()

    def update_header_rows(self):
        for row_no in range(self.header_row_count):
            for col_no in range(self.column_count):
                w = self.get_header_widget(self.screen_row_count, col_no)
                w.grid(row=row_no, column=col_no, sticky="nsew", pady=(0, 1), padx=(0, 1))
                w.configure(text=self.get_header_value(row_no, col_no))

        self.screen_row_count = self.header_row_count

    def get_data_widget(self, screen_row_no, col_no):
        if (screen_row_no, col_no) not in self.data_widgets:
            self.data_widgets[(screen_row_no, col_no)] = self.create_data_widget(col_no)

        return self.data_widgets[(screen_row_no, col_no)]

    def get_header_widget(self, row_no, col_no):
        if (row_no, col_no) not in self.header_widgets:
            self.header_widgets[(row_no, col_no)] = self.create_header_widget(col_no)

        return self.header_widgets[(row_no, col_no)]

    def create_data_widget(self, col_no):
        if col_no < self.frozen_column_count:
            background = None
        else:
            background = "white"

        return tk.Label(self, background=background, anchor="e", padx=7, text="")

    def create_header_widget(self, col_no):
        return tk.Label(self, anchor="e", padx=7, text="")

    def set_first_visible_data_row_no(self, n):
        self.first_visible_data_row_no = max(min(n, self.data_row_count), 0)
        self.update_screen_data()

    def _clear_screen_row(self, row_no):
        for widget in self.grid_slaves(row=row_no):
            widget.grid_remove()

    def update_screen_widgets(self, available_screen_height):
        max_screen_rows = available_screen_height // self.screen_row_height
        target_screen_row_count = max(
            min(
                max_screen_rows,
                self.header_row_count
                + self.data_row_count
                + self.footer_row_count
                - self.first_visible_data_row_no,
            ),
            self.header_row_count + 1 + self.footer_row_count,
        )
        # target_screen_row_count = 30

        # remove cells not required anymore ...
        while self.screen_row_count > target_screen_row_count:
            # print("removing")
            self._clear_screen_row(self.screen_row_count - 1)
            self.screen_row_count -= 1

        # ... or add cells that can be shown
        while self.screen_row_count < target_screen_row_count:
            # print("adding")
            for col in range(self.column_count):
                w = self.get_data_widget(self.screen_row_count, col)
                w.grid(
                    row=self.screen_row_count, column=col, sticky="nsew", pady=(0, 1), padx=(0, 1)
                )

            self.screen_row_count += 1

        self.visible_data_row_count = (
            self.screen_row_count - self.header_row_count - self.footer_row_count
        )

    def update_screen_data(self):
        self.update_screen_widgets(self.winfo_height())
        for screen_row_no in range(self.header_row_count, self.screen_row_count):
            data_row_no = self.first_visible_data_row_no + screen_row_no - self.header_row_count
            if data_row_no == self.data_row_count:
                break

            for col_no in range(self.column_count):
                w = self.get_data_widget(screen_row_no, col_no)
                value = self.get_data_value(data_row_no, col_no)
                if value is None:
                    w.configure(text="")
                else:
                    w.configure(text=str(value))

    def get_data_value(self, row_no, col_no):
        """lazy dict version:
        assert 0 <= row_no < self.data_row_count
        if row_no in self.data_rows:
            return self.data_rows[row_no][col_no]
        else:
            return ""
        """
        return self.data_rows[row_no][col_no]

    def get_header_value(self, row_no, col_no):
        return self.header_rows[row_no][col_no]

    def on_configure(self, event):
        # query row height
        _, _, _, height = self.grid_bbox(row=1)
        if height > 10 and height < 100:
            "self.screen_row_height = height + 2"

        # screen_available_height = self.winfo_height()

        # print("HE", self.winfo_height(), event.height, self.screen_row_height)
        self.update_screen_widgets(event.height)

        self.update_screen_data()


class ScrollableGridTable(ttk.Frame):
    def __init__(self, master, header_rows, data_row_count, footer_row_count, frozen_column_count):
        ttk.Frame.__init__(self, master)

        # set up scrolling with canvas
        hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, xscrollcommand=hscrollbar.set)
        get_workbench().bind_all("<Control-r>", self.debug)
        self.create_infopanel(data_row_count)
        hscrollbar.config(command=self.canvas.xview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.canvas.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        self.infopanel.grid(row=1, column=0, sticky=tk.NSEW)
        hscrollbar.grid(row=1, column=1, sticky=tk.NSEW)

        # vertical scrollbar performs virtual scrolling
        self.vscrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._handle_vertical_scroll
        )
        self.vscrollbar.grid(row=0, column=2, sticky=tk.NSEW)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.interior = ttk.Frame(self.canvas)
        self.interior.columnconfigure(0, weight=1)
        self.interior.rowconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.bind("<Configure>", self._configure_interior, True)
        self.bind("<Expose>", self._on_expose, True)

        self.grid_table = GridTable(
            self.interior, header_rows, data_row_count, footer_row_count, frozen_column_count
        )
        self.grid_table.grid(row=0, column=0, sticky=tk.NSEW)

        self._update_vertical_scrollbar()

    def debug(self, event=None):
        print("DE", self.vscrollbar.get())

    def create_infopanel(self, data_row_count):
        self.infopanel = ttk.Frame(self)
        self.size_label = ttk.Label(self.infopanel, text=str(data_row_count) + " rows")
        self.size_label.grid(row=0, column=0, padx=5)

    def _update_vertical_scrollbar(self):
        first = self.grid_table.first_visible_data_row_no / self.grid_table.data_row_count
        last = first + self.grid_table.visible_data_row_count / self.grid_table.data_row_count
        # print(first, last, self.grid_table.visible_data_row_count)
        self.vscrollbar.set(first, last)

    def _handle_vertical_scroll(self, *args):
        # print("vscroll", args, self.vscrollbar.get())
        if len(args) == 3 and args[0] == "scroll":
            amount = int(args[1])
            unit = args[2]
            if unit == "pages":
                amount *= self.grid_table.visible_data_row_count

            self.grid_table.set_first_visible_data_row_no(
                self.grid_table.first_visible_data_row_no + amount
            )
        else:
            assert args[0] == "moveto"
            pos = max(min(float(args[1]), 1.0), 0.0)
            top_row = math.floor(
                (self.grid_table.data_row_count - self.grid_table.visible_data_row_count + 1) * pos
            )
            self.grid_table.set_first_visible_data_row_no(top_row)

        self._update_vertical_scrollbar()

    def _on_expose(self, event):
        self.update_idletasks()
        self._configure_interior(event)

    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.canvas.winfo_height())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (
            self.interior.winfo_reqheight() != self.canvas.winfo_height()
            and self.canvas.winfo_height() > 10
        ):
            # update the interior's height to fit canvas
            self.canvas.itemconfigure(self.interior_id, height=self.canvas.winfo_height())

        self._update_vertical_scrollbar()
