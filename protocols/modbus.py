#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
modbus协议类
"""

import logging

from libs.base_protocol import BaseProtocol


logger = logging.getLogger('linkworld')


class ModbusProtocol(BaseProtocol):
    def process_data(self, device_info, data_msg):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        result = True
        if device_info is None:
            result = result and False

        device_data = data_msg

        return result, device_info, device_data

    def process_cmd(self, device_info, device_cmd):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        return device_cmd

