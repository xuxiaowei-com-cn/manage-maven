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
        # 添加处理程序
        logger.addHandler(sh)

    def window_resize(self, event=None):
        """
        窗口重置
        """
        if event is not None:
            if self.width != self.root.winfo_width():
                self.width = self.root.winfo_width()

                self.askdirectory_entry.config(width=int((self.root.winfo_width() - (70 + 2) - (91 + 2) - 10 * 2) / 7))
                self.username_entry.config(width=int((self.root.winfo_width() - (70 + 2) - (91 + 2) - 10 * 2) / 7))
                self.password_entry.config(width=int((self.root.winfo_width() - (70 + 2) - (91 + 2) - 10 * 2) / 7))
                self.upload_address_entry.config(
                    width=int((self.root.winfo_width() - (70 + 2) - (91 + 2) - 10 * 2) / 7))

                self.text_area.config(width=int((self.width - self.text_x * 2) / 7),
                                      height=int((self.height - self.text_y) / 14))

            if self.height != self.root.winfo_height():
                self.height = self.root.winfo_height()

                self.text_area.config(width=int((self.width - self.text_x * 2) / 7),
                                      height=int((self.height - self.text_y) / 14))

    def __init__(self):
        """
        初始化
        """
        self.__log__()

        self.root = tkinter.Tk()
        self.root.title("管理 Maven")

        # 窗口重置
        self.root.bind('<Configure>', self.window_resize)

        # 窗口大小
        self.width = 800
        self.height = 600

        # 按钮宽度
        self.button_width = 12

        # 文本 绝对位置
        self.text_x = 10
        self.text_y = 100

        x = self.root.winfo_screenwidth() / 2 - self.width / 2
        # 空出任务栏高度
        y = (self.root.winfo_screenheight() - 50) / 2 - self.height / 2

        # 设置窗口的大小与位置
        # self.root.geometry("800x600+368+107")
        self.root.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))
        # 最小屏幕
        self.root.minsize(self.width, self.height)
        # 最大屏幕
        # self.root.maxsize(self.width, self.height)

        # 创建一个Canvas
        # 设置其背景色为白色：bg='white'
        self.cv = tkinter.Canvas(self.root)

        # ipadx：X轴 内部填充
        # ipady：Y轴 内部填充
        # padx：X轴 外部填充
        # pady：Y轴 外部填充
        tkinter.Label(self.root, text="文件夹").grid(row=0, padx=14)

        # 上传文件夹输入框
        # 左侧 Label 设置 padx=14 时，宽度为 70（5倍）
        # 右侧按钮 91
        # 右侧按钮左右外边距 10
        # 边框 2
        self.askdirectory_entry = tkinter.Entry(self.root, state=tkinter.DISABLED,
                                                width=int((self.width - (70 + 2) - (91 + 2) - 10 * 2) / 7))
        self.askdirectory_entry.grid(row=0, column=1, pady=10)

        # 上传文件夹选择按钮
        self.askdirectory_button = tkinter.Button(self.root, text="选择文件夹", width=self.button_width,
                                                  command=self.askdirectory_command)
        self.askdirectory_button.grid(row=0, column=2, padx=10)

        tkinter.Label(self.root, text="用户名").grid(row=1)

        # 用户名输入框
        self.username_entry = tkinter.Entry(self.root, width=int((self.width - (70 + 2) - (91 + 2) - 10 * 2) / 7))
        self.username_entry.grid(row=1, column=1)

        tkinter.Label(self.root, text="密    码").grid(row=2)

        # 密码输入框
        self.password_entry = tkinter.Entry(self.root, width=int((self.width - (70 + 2) - (91 + 2) - 10 * 2) / 7),
                                            show='*')
        self.password_entry.grid(row=2, column=1)

        # 切换密码显示按钮
        self.password_show_button = tkinter.Button(self.root, text="显 示 密 码", width=self.button_width,
                                                   command=self.password_show_switch_command)
        self.password_show_button.grid(row=2, column=2)
        self.password_show_switch = False

        tkinter.Label(self.root, text="地    址").grid(row=3)

        # 上传地址输入框
        self.upload_address_entry = tkinter.Entry(self.root, width=int((self.width - (70 + 2) - (91 + 2) - 10 * 2) / 7))
        self.upload_address_entry.grid(row=3, column=1)

        # 上传按钮
        self.upload_button = tkinter.Button(self.root, text="上 传 文 件", width=self.button_width,
                                            command=self.upload_threading_command)
        self.upload_button.grid(row=3, column=2)

        # tkinter.Label(self.root, text="上传类型：").grid(row=4)

        # # 上传类型
        # self.upload_type_checkbutton = tkinter.Checkbutton(self.root, text='.jar')
        # self.upload_type_checkbutton.place(x=90, y=106)

        # 日志 文本
        self.text_area = tkinter.Text(self.root, bg='black', fg='white', width=int((self.width - self.text_x * 2) / 7),
                                      height=int((self.height - self.text_y) / 14))

        self.text_area.grid(row=4, columnspan=3, padx=self.text_x, pady=self.text_x)

        # 文本处理器
        text_handler = TextHandler(self.text_area)
        logger = logging.getLogger()
        logger.addHandler(text_handler)

        logging.info('程序启动...')
        logging.debug(f'日志目录：{self.LOGGING_DIRECTORY}')

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

    def __del__(self):
        logging.info('程序退出')


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
            self.text.insert(tkinter.END, f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}  {msg}\n')
            self.text.configure(state=tkinter.DISABLED)
            self.text.yview(tkinter.END)

        self.text.after(0, append)


if __name__ == '__main__':
    ManageMaven().root.mainloop()
