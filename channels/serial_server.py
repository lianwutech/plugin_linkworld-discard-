#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
串口通道类
"""

import logging

import serial

from libs.base_channel import BaseChannel


logger = logging.getLogger('yykj_serial')


class SerialChannel(BaseChannel):
    def __init__(self, network, channel_name, channel_protocol, channel_params, manager, channel_type):
        self.status = None
        self.port = channel_params.get("port", "")
        self.stopbits = channel_params.get("stopbits", serial.STOPBITS_ON)
        self.parity = channel_params.get("parity", serial.PARITY_NONE)
        self.bytesize = channel_params.get("bytesize", serial.EIGHTBITS)
        self.baudrate = channel_params.get("baudrate", 9600)
        self.timeout = channel_params.get("timeout", 1)
        BaseChannel.__init__(network, channel_name, channel_protocol, channel_params, manager, channel_type)

    def run(self):
        pass

    def send_cmd(self, device_info, device_cmd):
        pass