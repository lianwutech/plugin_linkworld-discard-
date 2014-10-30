#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
TCP-Client通道类
通过调用管理类对象的process_data函数实现信息的发送。
仅支持单个设备
"""

import time
import socket
import logging

from libs.base_channel import BaseChannel


logger = logging.getLogger('yykj_serial')


class TcpClientChannel(BaseChannel):
    def __init__(self, network, channel_name, channel_protocol, channel_params, manager, channel_type):
        self.status = None
        self.host = channel_params.get("host", "127.0.0.1")
        self.port = channel_params.get("port", 26)
        self.socket = None
        BaseChannel.__init__(self, network, channel_name, channel_protocol, channel_params, manager, channel_type)

    def run(self):
        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        try:
            self.socket.connect((self.host, self.port))
            while True:
                # 监听消息
                data = self.socket.recv(1024)
                if len(data) > 0:
                    data_msg = data
                    result = self.channel_manager.process_data(self.network_name,
                                                               self.channel_name,
                                                               self.channel_protocol,
                                                               None,
                                                               data_msg)
                    logger.debug("Process data result: %r" % result)
                else:
                    time.sleep(1)
                    logger.debug("No data, sleep 1s.")
        except Exception, e:
            logger.error("Socket error, error info:%r" % e)
            self.socket.close()
            self.socket = None

    def send_cmd(self, device_info, device_cmd):
        try:
            self.socket.send(device_cmd)
            return True
        except Exception, e:
            logger.error("Send_cmd error, error info:%r" % e)
            return False
