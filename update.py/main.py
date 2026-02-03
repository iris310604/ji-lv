import tkinter as tk
import subprocess
import queue
import threading
import os
# from tkinter import ttk

class Video:
    def __init__(self, root):
        self.root = root
        self.root.title('视频下载')
        self.root.geometry('480x300')
        #定义脚本字典：显示名称 -> 脚本文件名
        self.scripts_dict = {
            "B站视频": "b站.py",
            "腾讯视频": "腾讯.py"
        }
        #脚本选择变量 - 存储显示名称
        self.selected_display = tk.StringVar(value=list(self.scripts_dict.keys())[0])
        #实际的脚本文件名变量
        self.selected_script = tk.StringVar(value=list(self.scripts_dict.values())[0])
        self.create_widgets()
        #创建消息队列用于线程间通信
        self.message_queue = queue.Queue()

    def create_widgets(self):
        label_movie_link = tk.Label(self.root, text='输入视频网址:')
        label_movie_link.place(x=20, y=40, width=100, height=30)
        #输入窗口
        self.entry_movie_link = tk.Entry(self.root)
        self.entry_movie_link.place(x=120, y=40, width=330, height=30)
        #清空按钮
        button_clear = tk.Button(self.root, text='清空', command=self.empty)
        button_clear.place(x=380, y=100, width=70, height=30)  # 调整位置
        #按钮
        self.button_get = tk.Button(self.root, text='下载视频', command=self.get_video)
        self.button_get.place(x=30, y=150, width=420, height=30)
        #状态标签
        self.status_label = tk.Label(self.root, text="")
        self.status_label.place(x=50, y=200, width=400, height=30)
        #打开视频文件存放位置按钮
        self.button_open_video_path = tk.Button(self.root, text='打开目标文件夹', command=self.open_video_path)
        self.button_open_video_path.place(x=210, y=100, width=150, height=30)
        #脚本选择标签
        label_script = tk.Label(self.root, text='选择网站:')
        label_script.place(x=0, y=100, width=100, height=30)
        #创建下拉菜单，显示字典的键
        self.script_menu = tk.OptionMenu(
            self.root,
            self.selected_display,  # 绑定到显示名称变量
            *self.scripts_dict.keys(),  # 显示字典的键
            command=self.on_script_select  # 选择后更新脚本文件名
        )
        self.script_menu.place(x=80, y=100, width=120, height=30)
        # 双false窗口不能改变大小
        self.root.resizable(False, False)

    def on_script_select(self, display_name):
        """
        当下拉菜单选择改变时调用
        """
        #根据显示的友好名称获取实际的脚本文件名
        script_filename = self.scripts_dict.get(display_name, "b站.py")
        self.selected_script.set(script_filename)

    def open_video_path(self):
        video_path = '视频'
        #确保文件夹存在，如果不存在则创建
        if not os.path.exists(video_path):
            os.makedirs(video_path)
        #打开文件夹
        os.startfile(video_path)

    def empty(self):
        self.entry_movie_link.delete(0, 'end')

    def get_video(self):
        get_video_url = self.entry_movie_link.get()
        selected_display = self.selected_display.get()  #显示名称
        selected_script = self.selected_script.get()  #实际脚本文件名
        if get_video_url:
            #禁用按钮，防止重复点击
            # button_get = self.root.winfo_children()[3]  #按照按钮创造顺序获取按钮（废弃）
            self.button_get.config(state='disabled')    #定义一个按钮变量
            self.status_label.config(text="正在下载...", fg="black")

            #在线程中运行下载任务
            download_thread = threading.Thread(
                target=self.download_video_thread,
                args=(get_video_url, selected_script, selected_display),
                daemon=True
            )
            download_thread.start()

            #开始检查消息队列
            self.root.after(100, self.check_queue)
        else:
            self.status_label.config(text="请输入视频网址", fg="red")

    def download_video_thread(self, url, selected_script, selected_display):
        """
        在后台线程中运行下载任务
        """
        try:
            #运行py脚本
            result = subprocess.run(
                ["python", selected_script, url],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            #发送消息到队列
            if result.returncode == 0:
                self.message_queue.put(("success", "下载完成！"))
            else:
                error_msg = result.stderr if result.stderr else "下载失败"
                self.message_queue.put(("error", error_msg))

        except Exception as e:
            self.message_queue.put(("error", str(e)))

    def check_queue(self):
        """检查消息队列并更新UI"""
        try:
            #检查队列中是否有消息
            msg_type, message = self.message_queue.get_nowait()

            if msg_type == "success":
                self.status_label.config(text=message, fg='green')
            elif msg_type == "error":
                self.status_label.config(text=f"错误: {message}", fg='red')
            #重新启用按钮
            # button_get = self.root.winfo_children()[3]
            self.button_get.config(state='normal')

        except queue.Empty:
            #如果队列为空，100ms后再次检查
            self.root.after(100, self.check_queue)

if __name__ == '__main__':
    root = tk.Tk()
    app = Video(root)
    root.mainloop()

