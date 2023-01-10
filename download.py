# -*- coding:utf-8 -*-
import base64
import ctypes
import http.client
import logging.handlers
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup


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


def suffix(_url):
    """
    检查补充后缀
    """
    url_suffix = _url[len(_url) - 1:]
    if url_suffix != '/':
        return _url + "/"


def url_struct(_url, _href):
    href_split = str(_href).split("/")

    result_path_split = []

    point = 0
    for hs in href_split:
        if hs == '..':
            point += 1
        else:
            result_path_split.append(hs)

    url_split = _url.split("/")

    result_path_prefix = 0
    _url_split_len = len(url_split)
    for us in url_split:
        if result_path_prefix <= _url_split_len - point:
            result_path_split.insert(result_path_prefix, us)
        result_path_prefix += 1

    result_path = ''
    i = 0
    for tmp in result_path_split:
        if tmp == '':
            continue
        if i > 3:
            result_path += tmp + "/"
        i += 1

    url_urlparse = urlparse(_url)

    return url_urlparse.scheme + "://" + str(url_urlparse.hostname) + ":" + str(url_urlparse.port) + "/" + result_path


maven_url = "http://192.168.0.9:8081/repository/maven-upload"
username = 'admin'
password = 'xuxiaowei'

maven_url = suffix(maven_url)

_url = urlparse(maven_url)
hostname = str(_url.hostname)
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
                                     f"不支持协议：{scheme}\n不支持上传地址：{maven_url}".encode(
                                         'gbk'),
                                     "上传地址错误".encode('gbk'), 0x10)
    sys.exit()

authorization = basic(username, password)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.102 Safari/537.36',
    'Authorization': authorization
}

try:
    conn.request("GET", maven_url, headers=headers)
except Exception as e:
    logging.error(f'访问失败：{e}')
    sys.exit()

res = conn.getresponse()
read = res.read()
data = read.decode("utf-8")

soup = BeautifulSoup(data, 'html.parser')

aTags = soup.find_all('a', text='HTML index')
a = aTags[0]
href = a.attrs['href']

service_url = url_struct(maven_url, href)


def href_loop(_conn, _service_url, _headers):
    try:
        _conn.request("GET", _service_url, headers=_headers)
    except Exception as e:
        logging.error(f'访问失败：{e}')
        sys.exit()

    _res = _conn.getresponse()
    _read = _res.read()
    _data = _read.decode("utf-8")

    _soup = BeautifulSoup(_data, 'html.parser')
    _aTags = _soup.find_all('a')
    for _a in _aTags:
        _a_href = _a.attrs['href']
        if urlparse(_a_href).scheme == '':
            if _a_href == '../':
                continue
            _service_url_tmp = _service_url + _a_href
            href_loop(conn, _service_url_tmp, headers)
        else:
            print(str(_a_href).replace(maven_url, '') + '\t' + _a_href)


href_loop(conn, service_url, headers)