#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通道类
通过调用管理类对象的process_data函数实现信息的发送。
"""

import logging
import threading


logger = logging.getLogger('yykj_serial')


class BaseChannel(threading.Thread):
    """
    基础设备通信类
    针对每种通信模式实现各自的内容
    """

    def __init__(self, network_name, channel_name, channel_protocol, channel_params, channel_manager, channel_type):
        self.channel_name = channel_name
        self.channel_protocol = channel_protocol
        self.channel_params = channel_params
        self.network_name = network_name
        self.channel_manager = channel_manager
        self.channel_type = channel_type
        threading.Thread.__init__(self)

    def run(self):
        pass

    def send_cmd(self, device_info, device_cmd):
        pass
