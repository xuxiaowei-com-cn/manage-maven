# -*- coding:utf-8 -*-
import base64
import ctypes
import http.client
import logging.handlers
import os
import threading
import time
import tkinter.messagebox
from tkinter.filedialog import askdirectory
from urllib.parse import urlparse


def all_flie_path(path):
    """获取文件夹下所有的文件"""
    dir_paths = os.walk(path)
    result = []
    for root, dirs, files in dir_paths:
        for name in files:

            # 跳过文件
            if name == '_remote.repositories':
                continue
            elif name.startswith("maven-metadata") and (name.endswith(".xml") or name.endswith(".xml.sha1")):
                continue
            elif name.endswith('.part.lock'):
                continue
            elif name.endswith('.tmp'):
                continue
            elif name == 'resolver-status.properties':
                continue

            result.append(os.path.join(root, name))
    return result


def basic(username, password):
    """
    计算 basic
    :param username: 用户名
    :param password: 密码
    :return:
    """

    temp = username + ':' + password

    # 转 bytes
    temp_encode = temp.encode(encoding="utf-8")

    # base64 编码
    temp_b64encode = base64.b64encode(temp_encode)

    # base64 解码
    # temp_b64decode = base64.b64decode(temp_b64encode)

    return 'Basic ' + temp_b64encode.decode()


class ManageMaven:
    """
    管理 Maven
    """

    def __log__(self):
        """日志配置"""

        self.FMT = "%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"

        # 日志文件夹
        self.LOGGING_DIRECTORY = os.path.join(os.getenv("APPDATA"), 'manage_maven', 'log',
                                              time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

        # 判断文件是否不存在
        if not os.path.exists(self.LOGGING_DIRECTORY):
            # 创建文件夹
            os.makedirs(self.LOGGING_DIRECTORY)

        # 获取日志记录器
        logger = logging.getLogger()
        # 日志等级
        logger.setLevel(logging.DEBUG)

        # 全部日志
        all_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.LOGGING_DIRECTORY, 'all.log'))
        all_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(all_handler)

        # 正常日志
        into_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.LOGGING_DIRECTORY, 'info.log'))
        into_handler.setLevel(logging.INFO)
        into_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(into_handler)

        # 警告日志
        warning_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.LOGGING_DIRECTORY, 'warning.log'))
        warning_handler.setLevel(logging.WARNING)
        warning_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(warning_handler)

        # 异常日志
        error_handler = logging.FileHandler(os.path.join(self.LOGGING_DIRECTORY, 'error.log'))
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(error_handler)

        # 创建一个日志处理程序，用于将日志输出到控制台
        sh = logging.StreamHandler()
        # 设置输出到控制台的日志等级
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(logging.Formatter(self.FMT))
        # 添加处理程序
        logger.addHandler(sh)

    def window_resize(self, event=None):
        """
        窗口重置
        """
        if event is not None:
            if self.width != self.root.winfo_width():
                self.width = self.root.winfo_width()

                self.askdirectory_entry.config(width=self.entry_width())
                self.username_entry.config(width=self.entry_width())
                self.password_entry.config(width=self.entry_width())
                self.upload_address_entry.config(width=self.entry_width())

                self.text_area.config(width=self.text_width(), height=self.text_height())

            if self.height != self.root.winfo_height():
                self.height = self.root.winfo_height()

                self.text_area.config(width=self.text_width(), height=self.text_height())

    def on_closing(self):
        """
        退出前确认
        """
        if tkinter.messagebox.askokcancel("退出", "确定要退出？"):
            self.root.destroy()

    def __init__(self):
        """
        初始化
        """
        self.__log__()

        self.root = tkinter.Tk()
        self.root.title("管理 Maven")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 窗口重置
        self.root.bind('<Configure>', self.window_resize)

        # 窗口大小
        self.width = 800
        self.height = 600

        # 每行 X 轴方向：外部填充 4 像素
        self.frame_padx = 4
        # 每行 Y 轴方向：外部填充 4 像素
        self.frame_pady = 4
        # label：外部填充 4 像素
        self.label_padx = 4
        # label：宽度 41 像素：5 * 8 + 1
        self.label_width = 5
        # 按钮：宽度 73 像素：9 * 8 + 1
        self.button_width = 9

        # 窗口左上角坐标
        x = self.root.winfo_screenwidth() / 2 - self.width / 2
        # 空出任务栏高度：50
        y = (self.root.winfo_screenheight() - 50) / 2 - self.height / 2

        # 设置窗口的大小与位置
        self.root.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))
        # 最小屏幕
        self.root.minsize(self.width, self.height)

        # 第一行
        self.frame1 = tkinter.Frame(self.root)
        # 横向填充
        self.frame1.pack(fill=tkinter.X, padx=self.frame_padx, pady=self.frame_pady)

        # ipadx：X轴 内部填充
        # ipady：Y轴 内部填充
        # padx：X轴 外部填充
        # pady：Y轴 外部填充

        # 左对齐
        tkinter.Label(self.frame1, text="文件夹", width=self.label_width).pack(side=tkinter.LEFT, padx=self.label_padx)

        # 上传文件夹输入框
        self.askdirectory_entry = tkinter.Entry(self.frame1, state=tkinter.DISABLED, width=self.entry_width())
        self.askdirectory_entry.pack(side=tkinter.LEFT)

        # 上传文件夹选择按钮
        self.askdirectory_button = tkinter.Button(self.frame1, text="选择文件夹", width=self.button_width,
                                                  command=self.askdirectory_command)
        self.askdirectory_button.pack(side=tkinter.RIGHT)

        # 第二行
        self.frame2 = tkinter.Frame(self.root)
        # 横向填充
        self.frame2.pack(fill=tkinter.X, padx=self.frame_padx, pady=self.frame_pady)

        # 左对齐
        tkinter.Label(self.frame2, text="用户名", width=self.label_width).pack(side=tkinter.LEFT, padx=self.label_padx)

        # 用户名输入框
        self.username_entry = tkinter.Entry(self.frame2, width=self.entry_width())
        self.username_entry.pack(side=tkinter.LEFT)

        # 第三行
        self.frame3 = tkinter.Frame(self.root)
        # 横向填充
        self.frame3.pack(fill=tkinter.X, padx=self.frame_padx, pady=self.frame_pady)

        # 左对齐
        tkinter.Label(self.frame3, text="密   码", width=self.label_width).pack(side=tkinter.LEFT, padx=self.label_padx)

        # 密码输入框
        self.password_entry = tkinter.Entry(self.frame3, show='*', width=self.entry_width())
        self.password_entry.pack(side=tkinter.LEFT)

        # 切换密码显示按钮
        self.password_show_button = tkinter.Button(self.frame3, text="显 示 密 码", width=self.button_width,
                                                   command=self.password_show_switch_command)
        self.password_show_button.pack(side=tkinter.RIGHT)
        self.password_show_switch = False

        # 第四行
        self.frame4 = tkinter.Frame(self.root)
        # 横向填充
        self.frame4.pack(fill=tkinter.X, padx=self.frame_padx, pady=self.frame_pady)

        # 左对齐
        tkinter.Label(self.frame4, text="地   址", width=self.label_width).pack(side=tkinter.LEFT, padx=self.label_padx)

        # 上传地址输入框
        self.upload_address_entry = tkinter.Entry(self.frame4, width=self.entry_width())
        self.upload_address_entry.pack(side=tkinter.LEFT)

        # 上传按钮
        self.upload_button = tkinter.Button(self.frame4, text="上 传 文 件", width=self.button_width,
                                            command=self.upload_threading_command)
        self.upload_button.pack(side=tkinter.RIGHT)

        # 第五行
        self.frame5 = tkinter.Frame(self.root)
        # 横向填充
        self.frame5.pack(fill=tkinter.X, padx=self.frame_padx, pady=self.frame_pady)

        # 日志 文本
        self.text_area = tkinter.Text(self.frame5, bg='black', fg='white', width=self.text_width(),
                                      height=self.text_height())

        # 横向填充
        self.text_area.pack(side=tkinter.LEFT)

        # 滚动条
        self.scrollbar_y = tkinter.Scrollbar(self.frame5)
        # 右对齐，Y轴
        self.scrollbar_y.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # 滚动条控制文本
        self.scrollbar_y.config(command=self.text_area.yview)
        # 文本控制滚动条
        self.text_area.config(yscrollcommand=self.scrollbar_y.set)

        # 文本处理器
        text_handler = TextHandler(self.text_area)
        logger = logging.getLogger()
        text_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(text_handler)

        logging.info('程序启动...')
        logging.debug(f'日志目录：{self.LOGGING_DIRECTORY}')

    def entry_width(self):
        """
        计算输入框的宽度
        """
        sum_frame_padx = self.frame_padx * 2 + 1
        sum_label_padx = self.label_padx * 2 + 1
        sum_label_width = self.label_width * 8 + 1
        sum_button_width = self.button_width * 8 + 1
        return int((self.width - sum_frame_padx - sum_label_padx - sum_label_width - sum_button_width) / 7 - 1)

    def text_width(self):
        """
        计算文本框的宽度
        """
        sum_frame_padx = self.frame_padx * 2 + 1
        # Y 轴滚动条宽 17 像素
        scrollbar_y_width = 17
        return int((self.width - sum_frame_padx - scrollbar_y_width) / 7)

    def text_height(self):
        """
        计算文本框的高度
        """
        # 同时包含：输入框、按钮 的总高度
        sum_entry_button_height = 30 * 3
        # 仅包含：输入框 的总高度
        sum_entry_height = 23
        # 每行之间的间隔
        sum_interval_height = self.frame_pady * 5
        return int((self.height - sum_entry_button_height - sum_entry_height - sum_interval_height) / 13 - 1)

    def askdirectory_command(self):
        """
        打开文件夹
        :return:
        """
        ask_directory = askdirectory()
        logging.info(f'选择上传文件夹：{ask_directory}')

        if ask_directory != '':
            self.askdirectory_entry.config(state=tkinter.NORMAL)
            # 清空
            self.askdirectory_entry.delete(0, tkinter.END)
            # 将选择的文件夹放入文件夹输入框
            self.askdirectory_entry.insert(0, ask_directory)
            self.askdirectory_entry.config(state=tkinter.DISABLED)

    def password_show_switch_command(self):
        """
        切换密码显示
        """
        if self.password_show_switch:
            self.password_entry.config(show='*')
            self.password_show_button.config(text='显示密码')
            self.password_show_switch = False
        else:
            self.password_entry.config(show='')
            self.password_show_button.config(text='隐藏密码')
            self.password_show_switch = True

    def upload_threading_command(self):
        """
        使用线程执行
        """
        th = threading.Thread(target=self.upload_command)
        th.start()

    def upload_command(self):
        """
        上传
        :return:
        """

        if self.askdirectory_entry.get() == '':
            ctypes.windll.user32.MessageBoxA(0, f"上传文件夹不能为空".encode('gbk'), "上传文件夹错误".encode('gbk'), 0x10)
            return

        if self.upload_address_entry.get() == '':
            ctypes.windll.user32.MessageBoxA(0, f"上传地址不能为空".encode('gbk'), "上传地址错误".encode('gbk'), 0x10)
            return

        self.disabled()

        logging.info(f'上传文件夹：{self.askdirectory_entry.get()}')
        logging.info(f'上传用户名：{self.username_entry.get()}')
        logging.info(f'上传地址：{self.upload_address_entry.get()}')

        _url = urlparse(self.upload_address_entry.get())
        hostname = _url.hostname
        port = _url.port
        scheme = _url.scheme
        path = _url.path

        if scheme.lower() == 'http':
            conn = http.client.HTTPConnection(hostname, port)
        elif scheme.lower() == 'https':
            conn = http.client.HTTPSConnection(hostname, port)
        else:
            logging.error(f'协议：{scheme}')
            ctypes.windll.user32.MessageBoxA(0,
                                             f"不支持协议：{scheme}\n不支持上传地址：{self.upload_address_entry.get()}".encode('gbk'),
                                             "上传地址错误".encode('gbk'), 0x10)
            self.normal()
            return

        upload_files = all_flie_path(self.askdirectory_entry.get())

        authorization = basic(self.username_entry.get(), self.password_entry.get())

        headers = {
            'Authorization': authorization
        }

        for upload_file in upload_files:
            upload_file_relpath = os.path.relpath(upload_file, self.askdirectory_entry.get())

            payload = open(rf'{upload_file}', 'rb')

            conn.request("PUT", path + upload_file_relpath, payload, headers)
            res = conn.getresponse()
            data = res.read()

            if res.status == 201:
                logging.info(f'上传成功\t文件：{upload_file_relpath}')
            elif res.status == 400:
                logging.error(f'上传失败\t文件：{upload_file_relpath}')
            else:
                logging.warning(f'未知状态码\t文件：{upload_file_relpath}\tHTTP状态：{res.status}\tHTTP返回值：{data.decode("utf-8")}')

        self.normal()

    def disabled(self):
        """
        正在上传，禁用按钮与输入框
        """
        self.askdirectory_button.config(state=tkinter.DISABLED)
        self.username_entry.config(state=tkinter.DISABLED)
        self.password_entry.config(state=tkinter.DISABLED)
        self.password_show_button.config(state=tkinter.DISABLED)
        self.upload_address_entry.config(state=tkinter.DISABLED)
        self.upload_button.config(state=tkinter.DISABLED)
        self.upload_button.config(text='正在上传...')

    def normal(self):
        """
        上传完成，开放按钮与输入框
        """
        self.askdirectory_button.config(state=tkinter.NORMAL)
        self.username_entry.config(state=tkinter.NORMAL)
        self.password_entry.config(state=tkinter.NORMAL)
        self.password_show_button.config(state=tkinter.NORMAL)
        self.upload_address_entry.config(state=tkinter.NORMAL)
        self.upload_button.config(state=tkinter.NORMAL)
        self.upload_button.config(text='上传文件')

    # 禁用，防止使用 py2exe 打包，关闭软件时出现弹窗
    # def __del__(self):
    #     logging.info('程序退出')


class TextHandler(logging.Handler):
    """
    文本日志
    """

    def __init__(self, text):
        logging.Handler.__init__(self)
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state=tkinter.NORMAL)
            self.text.insert(tkinter.END, f'{msg}\n')
            self.text.configure(state=tkinter.DISABLED)
            self.text.yview(tkinter.END)

        self.text.after(0, append)


if __name__ == '__main__':
    ManageMaven().root.mainloop()
