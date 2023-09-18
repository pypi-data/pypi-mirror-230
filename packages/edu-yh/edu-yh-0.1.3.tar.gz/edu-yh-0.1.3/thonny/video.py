import os
import threading
import tkinter as tk
from tkinter import ttk

import vlc

from thonny.ui_utils import CommonDialog


class VideoDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master=master)
        self.title("视频播放器")
        self.geometry("900x650")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.instance = vlc.Instance("--no-xlib")
        self.player = self.instance.media_player_new()

        self.media = None
        self.media_path = ""
        self.playing = False
        self.display_volume = False

        self.current_time = "00:00"

        self.total_time = "00:00"

        self.playback_speed = 1.0  # 默认倍速为1x

        self.playing_lock = threading.Lock()

        self.style = ttk.Style()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.video_frame = ttk.Frame(self, borderwidth=1, relief="solid")
        self.bottom_frame = ttk.Frame(self, borderwidth=1, relief="solid")
        self.tree_frame = ttk.Frame(self)

        self.video_frame.place(relx=0, rely=0, relwidth=0.75, relheight=0.75)
        self.bottom_frame.place(relx=0, rely=0.75, relwidth=0.75, relheight=0.25)
        self.tree_frame.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

        self.tree_frame.rowconfigure(0, weight=1)  # 设置第0行的权重，以填充垂直空间

        self.vlc_player = self.instance.media_player_new()
        self.vlc_player.set_fullscreen(False)
        self.vlc_player.set_hwnd(self.video_frame.winfo_id())
        self.vlc_player.audio_set_volume(50)

        # 图像引入
        img_dir = os.path.join(os.path.dirname(__file__), "res")
        self.video_play = tk.PhotoImage("video_play", file=os.path.join(img_dir, "video-play.png"))

        self.video_stop = tk.PhotoImage("video_stop", file=os.path.join(img_dir, "video-stop.png"))

        self.video_rewind = tk.PhotoImage(
            "video_rewind", file=os.path.join(img_dir, "video-rewind.png")
        )

        self.video_fast_forward = tk.PhotoImage(
            "video_fast_forward", file=os.path.join(img_dir, "video-fast-forward.png")
        )

        self.video_mute = tk.PhotoImage("video_mute", file=os.path.join(img_dir, "video-mute.png"))

        self.video_voice = tk.PhotoImage(
            "video_voice", file=os.path.join(img_dir, "video-voice.png")
        )

        self.current_time_label = tk.Label(self.bottom_frame, text=self.current_time)
        self.current_time_label.place(relx=0.20, rely=0.2, relheight=0.1, relwidth=0.06)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.bottom_frame, variable=self.progress_var, maximum=100, mode="determinate"
        )
        self.progress_bar.place(relx=0.27, rely=0.24, relheight=0.04, relwidth=0.46)
        self.progress_bar.bind("<Button-1>", self.seek_to_progress)
        self.progress_bar["style"] = "TProgressbar"

        self.progress_bar.rowconfigure(0, weight=1)  # 设置第0行的权重，以填充垂直空间

        self.total_time_label = tk.Label(self.bottom_frame, text=self.total_time, anchor="w")
        self.total_time_label.place(relx=0.74, rely=0.2, relheight=0.1, relwidth=0.062)

        self.playback_speed_var = tk.StringVar(value=str(self.playback_speed) + "x")

        self.playback_speed_menu = ttk.Combobox(
            self.bottom_frame,
            textvariable=self.playback_speed_var,
            values=["0.5x", "1.0x", "2.0x"],
            state="readonly",
        )
        self.playback_speed_menu.place(relx=0.12, rely=0.51, relheight=0.22, relwidth=0.1)
        self.playback_speed_menu.bind("<<ComboboxSelected>>", self.update_playback_speed)

        self.rewind_button = ttk.Button(
            self.bottom_frame, image=self.video_rewind, command=self.rewind
        )
        self.rewind_button.place(relx=0.3, rely=0.5, relheight=0.25, relwidth=0.1)

        self.play_pause_button = ttk.Button(
            self.bottom_frame, image=self.video_play, command=self.play_pause
        )
        self.play_pause_button.place(relx=0.45, rely=0.5, relheight=0.25, relwidth=0.1)

        self.fast_forward_button = ttk.Button(
            self.bottom_frame, image=self.video_fast_forward, command=self.fast_forward
        )
        self.fast_forward_button.place(relx=0.6, rely=0.5, relheight=0.25, relwidth=0.1)

        self.voice_button = ttk.Button(
            self.bottom_frame, image=self.video_voice, command=self.show_volume
        )
        self.voice_button.place(relx=0.77, rely=0.5, relheight=0.25, relwidth=0.1)
        # 音量滑块
        self.volume_slider = ttk.Scale(
            self.bottom_frame, from_=0, to=100, orient="horizontal", command=self.update_volume
        )
        self.volume_slider.set(50)  # 初始音量为50
        self.volume_slider.place_forget()

        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Path"))
        self.tree.heading("#0", text="Name")
        self.tree.heading("#1", text="Type")
        self.tree.heading("#2", text="Path")
        self.tree.column("#1", width=0)  # 隐藏第一列
        self.tree.column("#2", width=0)  # 隐藏第二列
        self.tree.place(relx=0, rely=0, relwidth=0.9, relheight=1)

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.place(relx=0.9, rely=0, relwidth=0.1, relheight=1)

        self.tree.configure(yscrollcommand=self.scrollbar.set)

        file_path = "../video"
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        self.populate_tree("", file_path)  # 替换为实际的文件夹路径

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.playback_index = 0

    def show_volume(self):
        if not self.display_volume:
            self.volume_slider.place(relx=0.67, rely=0.4, relheight=0.05, relwidth=0.3)
        else:
            self.volume_slider.place_forget()
        self.display_volume = not self.display_volume

    def update_volume(self, volume):
        volume = int(float(volume))
        self.vlc_player.audio_set_volume(volume)

    def update_playback_speed(self, event):
        speed_str = self.playback_speed_var.get()
        speed = float(speed_str.replace("x", ""))
        self.playback_speed = speed

        if self.vlc_player.get_rate() != self.playback_speed:
            self.vlc_player.set_rate(self.playback_speed)

    def seek_to_progress(self, event):
        if self.media is not None:
            progress_width = self.progress_bar.winfo_width()
            click_x = event.x
            seek_time = int((click_x / progress_width) * self.vlc_player.get_length())
            self.vlc_player.set_time(seek_time)

    def populate_tree(self, parent, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                node = self.tree.insert(parent, "end", text=item, values=("folder", item_path))
                self.populate_tree(node, item_path)
            elif item.lower().endswith((".mp4", ".avi", ".mkv")):
                self.tree.insert(parent, "end", text=item, values=("file", item_path))

    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        item_type = self.tree.set(item, "#1")

        if item_type == "file":
            self.media_path = self.tree.set(item, "#2")
            if self.media_path.lower().endswith((".mp4", ".avi", ".mkv")):
                self.playing = False
                self.media = self.instance.media_new(self.media_path)
                self.vlc_player.set_media(self.media)
                self.play_pause()

    def play_pause(self):
        if self.media is not None:
            if self.playing:
                self.vlc_player.pause()
                self.play_pause_button.config(image=self.video_play)
                self.playing = False  # 停止播放状态
            else:
                self.vlc_player.play()
                self.play_pause_button.config(image=self.video_stop)
                self.after(500, self.update_labels_in_main_thread)
                self.playing = True  # 标记为播放状态

    def rewind(self):
        if self.media is not None:
            current_time = self.vlc_player.get_time()
            self.vlc_player.set_time(max(0, current_time - 10000))

    def fast_forward(self):
        if self.media is not None:
            current_time = self.vlc_player.get_time()
            self.vlc_player.set_time(current_time + 10000)

    def play_next(self):
        selected_item = self.tree.selection()
        next_item = self.tree.next(selected_item[0])
        while next_item:
            item_type = self.tree.set(next_item, "#1")
            if item_type == "file":
                self.playing = False
                self.tree.selection_set(next_item)
                self.media_path = self.tree.set(next_item, "#2")
                self.media = self.instance.media_new(self.media_path)
                self.vlc_player.set_media(self.media)
                self.play_pause()  # Directly call play_pause to play the next video
                return
            next_item = self.tree.next(next_item)

        # If no more file items are found, stop playback
        self.playing = False
        self.play_pause_button.config(image=self.video_play)
        self.progress_var.set(0)
        self.media = None  # Reset the media instance after all videos have been played

    def update_labels_in_main_thread(self):
        if self.playing:
            current_time = self.vlc_player.get_time()
            total_time = self.vlc_player.get_length()
            current_time_str = self.format_time(current_time)
            total_time_str = self.format_time(total_time)
            self.current_time_label.config(text=current_time_str)
            self.total_time_label.config(text=total_time_str)
            self.after(500, self.update_labels_in_main_thread)  # 再次调度更新

            if total_time > 0:
                progress = (current_time / total_time) * 100
                self.progress_var.set(progress)
            if current_time >= total_time:
                self.play_next()

    def format_time(self, milliseconds):
        total_seconds = int(milliseconds / 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def on_closing(self):
        if self.playing:
            self.vlc_player.stop()  # 停止音频播放
            self.playing = False  # 停止播放线程的执行
        self.destroy()  # 销毁窗口
