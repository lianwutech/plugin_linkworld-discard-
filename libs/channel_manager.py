#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通道管理类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
支持的通道类型有Serial、HttpServer、TcpServer、UdpServer、HttpClient、TcpClient、UdpClient
"""

import os
import sys

from libs.base_channel import *
from libs.utils import cur_file_dir, get_subclass


class ChannelManager(object):
    def __init__(self, plugin_manager):
        self.mapper_dict = dict()
        self.channel_class_dict = dict()
        self.channel_dict = dict()
        self.channel_device_dict = dict()
        self.plugin_manager = plugin_manager

    def load(self, plugin_params):
        # 扫描通道库
        # 通过扫描目录来获取支持的协议库
        cur_dir = cur_file_dir()
        if cur_dir is not None:
            channel_lib_path = cur_dir + "/channels"
            file_list = os.listdir(channel_lib_path)
            for file_name in file_list:
                file_path = os.path.join(channel_lib_path, file_name)
                if os.path.isfile(file_path) and ".py" in file_name:
                    channel_name, ext = os.path.splitext(file_name)
                    # 确保协议名称为小写
                    channel_name = channel_name.lower()
                    # 加载库
                    module_name = "channels." + channel_name
                    module = __import__(module_name)
                    channel_module_attrs = getattr(module, channel_name)
                    class_object = get_subclass(channel_module_attrs, BaseChannel)
                    self.channel_class_dict[channel_name] = class_object
        # 加载参数
        for device_network in plugin_params:
            network_name = device_network.get("network_name", "")
            protocol = device_network.get("protocol", "").lower()
            channels = device_network.get("channels", [])
            for channel in channels:
                channel_name = channel.get("name", "")
                channel_type = channel.get("type", "")
                channel_params = channel.get("params", "{}")
                preconfigured_devices = channel.get("preconfigured_devices", [])

                # 创建通道对象
                if channel_type in self.channel_class_dict:
                    channel_class_object = self.channel_class_dict[channel_type]
                    self.channel_dict[channel_name] = channel_class_object(network_name,
                                                                           channel_name,
                                                                           protocol,
                                                                           channel_params,
                                                                           self,
                                                                           channel_type)
                else:
                    logger.error("channel type(%s) is not exist. Please check!" % channel_name)
                    sys.exit(1)

                # 通道启动
                try:
                    self.channel_dict[channel_name].start()
                except Exception, e:
                    logger.error("channel(%s) run fail. error info: %r" % (channel_name, e))

                # 通道与设备的映射管理建立
                self.channel_device_dict[channel_name] = dict()
                for device_info in preconfigured_devices:
                    device_id = "%s/%s/%s" % (network_name,
                                              device_info.get("device_addr", ""),
                                              device_info.get("device_port"))
                    device_info["device_id"] = device_id
                    if "protocol" not in device_info:
                        device_info["protocol"] = protocol
                    device_info["channel"] = channel_name
                    self.mapper_dict[device_id] = channel_name
                    self.channel_device_dict[channel_name][device_id] = device_info

        # 检查通道启动情况，如果有通道退出，则系统退出。
        for channel_name in self.channel_dict:
            if not self.channel_dict[channel_name].isAlive():
                logger.fatal("channel(%s) is not run. please check。" % channel_name)
                sys.exit(1)

    def add_device(self, channel_name, device_id, device_info):
        if device_id in self.mapper_dict:
            if channel_name in self.channel_dict:
                self.channel_device_dict[channel_name][device_id] = device_info
                self.mapper_dict[device_id] = channel_name
                return True
            else:
                logger.error("channel(%s) is not exist." % channel_name)
                return False
        else:
            logger.info("device(%s) is exist." % device_id)
            return False

    def process_data(self, network_name, channel_name, channel_protocol, device_id, data_msg):
        """
        所有通道共用的数据处理通道
        :param channel:
        :param protocol:
        :param msg:
        :return:
        """
        if device_id is None or device_id not in self.channel_device_dict[channel_name]:
            result, device_info, device_data = self.plugin_manager.process_data_by_protocol(channel_protocol, data_msg)
            if result:
                # 协议处理成功
                if device_info is None:
                    if len(self.channel_device_dict[channel_name]) == 1:
                        for key, value in self.channel_device_dict[channel_name].items():
                            device_id = key
                    else:
                        logger.error("device not decide.")
                        return False
                else:
                    device_id = "%s/%s/%s" % (network_name,
                                              device_info.get("device_addr", ""),
                                              device_info.get("device_port"))
                    device_info["device_id"] = device_id

                    # 判断设备是否存在，没有则新增设备
                    if device_id not in self.channel_device_dict[channel_name]:
                        self.plugin_manager.add_device(network_name, channel_name, channel_protocol, device_id,
                                                       device_info)
            else:
                # 协议处理失败
                logger.error("protocol process fails. protocol:%s, data_msg:%r" % (channel_protocol, data_msg))
                return False
        else:
            device_data = self.plugin_manager.process_data(device_id, data_msg)

        # 发送数据
        return self.plugin_manager.send_data(device_id, device_data)

    def send_cmd(self, device_id, device_cmd):
        if device_id in self.mapper_dict:
            channel_name = self.mapper_dict[device_id]
            device_info = self.channel_device_dict[channel_name][device_id]
            if channel_name in self.channel_dict:
                channel = self.channel_dict.get(channel_name, None)
                if not channel.isAlive():
                    logger.error("channel(%s) is not alive, restart." % channel_name)
                    channel.run()
                # 消息发送
                return channel.send_cmd(device_info, device_cmd)
            else:
                logger.error("channel(%s) is not exist." % channel_name)
                return False
        else:
            logger.error("device(%s) is not exist." % device_id)
            return False

    def check_status(self):
        """
        检查通道运行状态
        :return:
        """
        status_dict = dict()
        for channel_name in self.channel_dict:
            if self.channel_dict[channel_name].isAlive():
                status_dict[channel_name] = "run"
            else:
                status_dict[channel_name] = "stop"
                logger.error("channel(%s) is not alive, restart." % channel_name)
                old_channel = self.channel_dict[channel_name]
                if old_channel.channel_type in self.channel_class_dict:
                    channel_class_object = self.channel_class_dict[old_channel.channel_type]
                    new_channel = channel_class_object(old_channel.network_name,
                                                       old_channel.channel_name,
                                                       old_channel.channel_protocol,
                                                       old_channel.channel_params,
                                                       old_channel.channel_manager,
                                                       old_channel.channel_type)
                    self.channel_dict[channel_name] = new_channel
                    self.channel_dict[channel_name].start()
                else:
                    logger.error("不可能发生的错误。")

        return status_dict
