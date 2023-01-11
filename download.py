# -*- coding:utf-8 -*-
import base64
import ctypes
import http.client
import logging.handlers
import os
import sys
import urllib.request
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
    return _url


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
download_path = 'D:\\Apache\\download_path'

maven_url = suffix(maven_url)
download_path = suffix(download_path)

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
    ctypes.windll.user32.MessageBoxA(0, f"不支持协议：{scheme}\n不支持下载地址：{maven_url}".encode('gbk'),
                                     "地址错误".encode('gbk'), 0x10)
    sys.exit()

authorization = basic(username, password)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.102 Safari/537.36'
}

if username != '' or password != '':
    logging.info(f'使用用户名和密码')
    # oss.sonatype.org 域名推荐缺省密码
    headers['Authorization'] = authorization
else:
    logging.info(f'未使用用户名和密码')

try:
    conn.request("GET", maven_url, headers=headers)
except Exception as e:
    logging.error(f'访问失败：{e}')
    sys.exit()

res = conn.getresponse()

if res.status == 401:
    ctypes.windll.user32.MessageBoxA(0, f"用户名或密码不正确".encode('gbk'), "凭证错误".encode('gbk'), 0x10)
    sys.exit()

read = res.read()
data = read.decode("utf-8")

soup = BeautifulSoup(data, 'html.parser')

title = soup.find('title').text
if title == 'Access Denied':
    ctypes.windll.user32.MessageBoxA(0, f"用户名或密码不正确".encode('gbk'), "凭证错误".encode('gbk'), 0x10)
    sys.exit()

aTags = soup.find_all('a', text='HTML index')

# 兼容 oss.sonatype.org 与自己搭建的 nexus
if len(aTags) == 0:
    service_url = maven_url
else:
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

        # 兼容 oss.sonatype.org 与自己搭建的 nexus
        elif _a_href[len(_a_href) - 1:] == '/':
            if urlparse(_a_href).scheme == '':
                _service_url_tmp = _service_url + _a_href
                href_loop(conn, _service_url_tmp, headers)
            else:
                href_loop(conn, _a_href, headers)

        else:
            file_path = download_path + _a_href.replace(":/", '').replace(":", "/")
            disk_path = os.path.dirname(os.path.abspath(file_path))
            if not os.path.exists(disk_path):
                os.makedirs(disk_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            print(disk_path + '\t' + _a_href)
            urllib.request.urlretrieve(_a_href, filename=file_path)


href_loop(conn, service_url, headers)
