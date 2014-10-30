#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
基础协议类
"""


class BaseProtocol(object):
    def process_data(self, device_info, data_msg):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        return None, None

    def process_cmd(self, device_info, device_cmd):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        return None

