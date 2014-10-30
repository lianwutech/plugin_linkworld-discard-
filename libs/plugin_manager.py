#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
插件管理类
内部包含3个对象：通道管理对象、MQTT管理对象、协议管理对象
内部基于device_id进行协调
通道管理对象实现指令发送
MQTT管理对象实现数据发送
协议管理对象实现消息的编解码
每个管理对象内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
插件管理类管理整个设备信息
"""

from channel_manager import *
from mqtt_manager import *
from protocol_manager import *

from libs import const


logger = logging.getLogger('yykj_serial')
const.devices_file_name = "devices.txt"


class PluginManager(object):
    def __init__(self):
        self.channel_manager = None
        self.protocol_manager = None
        self.mqtt_manager = None
        # 使用channel_manager的设备字典作为插件的字典
        # self.devices_dict = dict()
        self.plugin_params = None

    def load(self, plugin_params):
        """
        加载参数
        :param params:
        :return:
        """
        self.plugin_params = plugin_params
        # 启动顺序，协议管理对象、Mqtt管理对象、通道管理对象
        self.protocol_manager = ProtocolManger(self)
        result = self.protocol_manager.load(plugin_params)
        if result is False:
            logger.error("Load protocol manager fail.")
            sys.exit(1)
        self.mqtt_manager = MQTTManager(self)
        self.mqtt_manager.load(plugin_params)
        if result is False:
            logger.error("Load mqtt manager fail.")
            sys.exit(1)
        self.channel_manager = ChannelManager(self)
        self.channel_manager.load(plugin_params)
        if result is False:
            logger.error("Load channel manager fail.")
            sys.exit(1)

    def add_device(self, network_name, channel_name, protocol_name, device_id, device_info):
        # 插件管理类不保留设备信息，使用channal_manager的设备字典
        # 将设备信息插入到Mqtt管理对象
        self.mqtt_manager.add_device(network_name, device_id, device_info)
        # 将设备信息插入到通道管理对象
        self.channel_manager.add_device(channel_name, device_id, device_info)
        self.protocol_manager.add_device(protocol_name, device_id, device_info)
        # 写设备信息文件
        devices_file_name = const.devices_file_name
        devices_file = open(devices_file_name, "w+")
        devices_file.write(json.dumps(self.channel_manager.device_dict))
        devices_file.close()
        return True

    def send_cmd(self, device_id, device_cmd):
        return self.channel_manager.send_cmd(device_id, device_cmd)

    def send_data(self, device_id, device_data):
        return self.mqtt_manager.send_data(device_id, device_data)

    def process_data(self, device_id, data_msg):
        """
        返回device_data
        :param device_id:
        :param data_msg:
        :return:设备数据
        """
        return self.protocol_manager.process_data(device_id, data_msg)

    def process_cmd(self, device_id, device_cmd):
        """
        返回cmd_msg
        :param device_id:
        :param device_cmd:
        :return:设备消息
        """
        return self.protocol_manager.process_cmd(device_id, device_cmd)

    def process_data_by_protocol(self, protocol, data_msg):
        """
        返回device_data
        :param channel:
        :param protocol:
        :param data_msg:
        :return:处理结果、设备信息、设备数据
        """
        # 获取设备信息
        #
        return self.protocol_manager.process_data_by_protocol(protocol, data_msg)

    def check_channel_status(self):
        return self.channel_manager.check_status()

    def check_mqtt_client_status(self):
        return self.mqtt_manager.check_status()

