#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
协议管理类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
"""

import os
import logging

from libs.base_protocol import BaseProtocol
from utils import cur_file_dir, get_subclass


logger = logging.getLogger('yykj_serial')


class ProtocolManger(object):
    def __init__(self, plugin_manager):
        self.mapper_dict = dict()
        self.protocol_dict = dict()
        self.protocol_class_dict = dict()
        self.device_dict = dict()
        self.plugin_manager = plugin_manager

    def load(self, plugin_params):
        # 通过扫描目录来获取支持的协议库
        cur_dir = cur_file_dir()
        if cur_dir is not None:
            protocol_lib_path = cur_dir + "/protocols"
            file_list = os.listdir(protocol_lib_path)
            for file_name in file_list:
                file_path = os.path.join(protocol_lib_path, file_name)
                if os.path.isfile(file_path) and \
                                ".py" in file_name and \
                                "__" not in file_name and \
                                ".pyc" not in file_name:
                    protocol_name, ext = os.path.splitext(file_name)
                    # 确保协议名称为小写
                    protocol_name = protocol_name.lower()
                    # 加载库
                    module_name = "protocols." + protocol_name
                    try:
                        module = __import__(module_name)
                        # class_name = words_capitalize(protocol_name, "_") + "Protocol"
                        # class_object = getattr(module, class_name)
                        protocol_module = getattr(module, protocol_name)
                        class_object = get_subclass(protocol_module, BaseProtocol)
                        if class_object is not None:
                            self.protocol_class_dict[protocol_name] = class_object
                            self.protocol_dict[protocol_name] = class_object()
                            logger.debug("Load protocol(%s) success." % module_name)
                        else:
                            logger.error("protocol(%s) has not protocol sub class." % module_name)
                            return False
                    except Exception, e:
                        logger.error("Load protocol(%s) fail, error info:%r" % (module_name, e))
                        return False

        # 根据配置生成具体对象
        for device_network in plugin_params:
            network_name = device_network.get("network_name", "")
            protocol = device_network.get("protocol", "").lower()
            # 确保协议类型字段存在
            if len(protocol) > 0:
                channels = device_network.get("channels", [])
                for channel in channels:
                    # 协议库存在则创建对应映射记录
                    preconfigured_device_list = channel.get("preconfigured_devices", [])
                    for device_info in preconfigured_device_list:
                        device_id = "%s/%s/%s" % (network_name,
                                                  device_info.get("device_addr", ""),
                                                  device_info.get("device_port"))
                        device_info["device_id"] = device_id
                        device_protocol_type = device_info.get("protocol", protocol)
                        device_info["protocol"] = device_protocol_type
                        if device_protocol_type in self.protocol_dict:
                            self.mapper_dict[device_id] = device_protocol_type
                            self.device_dict[device_id] = device_info
                        else:
                            # 有协议库不存在，系统退出
                            logger.error("protocol(%s) lib don't exit." % device_protocol_type)
                            return False
            else:
                logger.error("params error. protocol_type is null.")
                return False
        return True

    def add_device(self, protocol_type, device_id, device_info):
        if protocol_type in self.protocol_dict:
            self.device_dict[device_id] = device_info
            self.mapper_dict[device_id] = protocol_type
            return True
        else:
            logger.error("Protocol(%s) is not exist." % protocol_type)
            return False

    def process_data(self, device_id, msg):
        """
        根据device_id进行数据处理，生成数据
        :param device_id:
        :param msg:
        :return:设备数据
        """
        if device_id in self.mapper_dict:
            protocol_type = self.mapper_dict[device_id]
            device_info = self.device_dict.get(device_id, None)
            if protocol_type in self.protocol_dict:
                result, device_info, device_data = self.protocol_dict[protocol_type].process_data(device_info, msg)
                return device_data
            else:
                logger.error("fatal error，protocol(%s) is lost。" % protocol_type)
                return None
        else:
            logger.info("device_id(%s) is not exist")
            return None

    def process_cmd(self, device_id, msg):
        """
        根据device_id进行命令处理，生成要发送的命令字
        :param device_id:
        :param msg:
        :return: 设备消息
        """
        if device_id in self.mapper_dict:
            protocol_type = self.mapper_dict[device_id]
            device_info = self.device_dict.get(device_id, None)
            return self.protocol_dict[protocol_type].process_cmd(device_info, msg)
        else:
            logger.info("device_id(%s) is not exist" % device_id)
            return None

    def process_data_by_protocol(self, protocol, msg):
        """
        根据协议类型来进行消息处理，返回设备信息和数据。
        :param protocol_type:
        :param msg:
        :return: 处理结果、设备信息、设备数据
        """
        if protocol in self.protocol_dict:
            return self.protocol_dict[protocol].process_data(None, msg)
        else:
            logger.info("protocol_type(%s) is not exist" % protocol)
            return False, None, None
