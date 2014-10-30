#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
YYkj协议类
"""

import logging

from libs.base_protocol import BaseProtocol


logger = logging.getLogger('yykj_serial')


class YykjProtocol(BaseProtocol):
    def process_data(self, device_info, data_msg):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        result = True
        device_data = data_msg

        if "01:Begin" in device_data:
            # 开始消息忽略
            device_data = None
        elif "01:StudyOK" in device_data:
            device_data = "01:StudyOK"
        elif "01:StudyER" in device_data:
            device_data = "01:StudyER"
        elif "01:Send_OK" in device_data:
            device_data = "01:Send_OK"
        elif "01:Send_ER" in device_data:
            device_data = "01:Send_ER"
        else:
            logger.error("Unknown infrared message(%s). " % device_data)
            # 错误消息忽略
            device_data = None

        return result, device_info, device_data

    def process_cmd(self, device_info, device_cmd):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        device_cmd = device_cmd.strip()
        if len(device_cmd) != 6 or ('S' not in device_cmd and 'F' not in device_cmd):
            device_cmd = None
        return device_cmd

