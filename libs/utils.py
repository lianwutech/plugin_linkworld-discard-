#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys


def int2hex(int_value, sizeofint=2):
    """
    整形转hex字符串
    :param int_value:
    :return: hex字符串，不包含前缀
    """
    negativ_int_cal_num = int("0x" + "FF" * sizeofint, 16)
    encoded = format(int_value & negativ_int_cal_num, 'x')
    length = len(encoded)
    encoded = encoded.zfill(length + length % 2)
    return encoded


# 16进制字符串转整形
def hex2int(hex_str):
    return hex_str.decode('hex')


# 获取脚本文件的当前路径
def cur_file_dir():
    # 获取脚本路径
    path = sys.path[0]
    # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


# 获取本机IP地址
def get_ip_addr(ifname="eth0"):
    import platform

    system = platform.system()
    if system == "Windows" or system == "Darwin":
        import socket
        # 获取本机电脑名
        myname = socket.getfqdn(socket.gethostname())
        # 获取本机ip
        myaddr = socket.gethostbyname(myname)
        return myaddr
    elif system == "Linux":
        import socket
        import fcntl
        import struct

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915,  # SIOCGIFADDR
                                            struct.pack('256s', ifname[:15])
        )[20:24])
    else:
        return "127.0.0.1"


def words_capitalize(words_str, split_char):
    """
    根据分割字符对字符串进行首字母大写并连接
    :param str:
    :param split_char:
    :return:
    """
    result_str = ""
    word_list = words_str.split(split_char)
    for word in word_list:
        result_str = result_str + word.capitalize()
    return result_str


def get_subclass(module, base_class):
    """
    获取子类的对象
    :param module:
    :param base_class:
    :return:
    """
    for name in dir(module):
        obj = getattr(module, name)
        try:
            if issubclass(obj, base_class) and obj != base_class:
                return obj
        except TypeError:  # If 'obj' is not a class
            pass
    return None


def convert(input):
    """
    将字典或列表中unicode转成utf-8
    :param input:
    :return:
    """
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input