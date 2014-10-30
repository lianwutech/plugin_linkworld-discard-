#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
MQTT管理类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
"""
import sys

from mqttclient import *


# 日志对象
logger = logging.getLogger('yykj_serial')


class MQTTManager(object):
    def __init__(self, plugin_manager):
        self.mapper_dict = dict()
        self.mqtt_dict = dict()
        # self.device_dict = dict()
        self.plugin_manager = plugin_manager

    def load(self, plugin_params):
        # 根据device_network来创建Mqtt客户端
        for device_network in plugin_params:
            network_name = device_network.get("network_name", "")
            self.mqtt_dict[network_name] = MqttClient(network_name, device_network, self.plugin_manager)
            self.mqtt_dict[network_name].start()
            channels = device_network.get("channels", [])
            for channel in channels:
                preconfigured_devices = channel.get("preconfigured_devices", [])
                for device_info in preconfigured_devices:
                    device_id = "%s/%s/%s" % (network_name,
                                              device_info.get("device_addr", ""),
                                              device_info.get("device_port"))
                    self.mapper_dict[device_id] = network_name

        # 如果MQTT服务器没启动，则系统退出。
        for network_name in self.mqtt_dict:
            if not self.mqtt_dict[network_name].isAlive():
                logger.fatal("network(%s) is not run. please check。" % network_name)
                sys.exit(1)

    def send_data(self, device_id, device_data):
        if device_id in self.mapper_dict:
            network_name = self.mapper_dict[device_id]
            if network_name in self.mqtt_dict:
                client = self.mqtt_dict[network_name]
                return client.send_data(device_id, device_data)
            else:
                logger.error("network(%s) is not exist." % network_name)
                return False
        else:
            logger.error("device(%s) is not exist." % device_id)
            return False

    def send_data_by_protocol(self, protocol, msg):
        device_info, device_data = self.plugin_manager.process_data_by_type(protocol, msg)
        pass

    def add_device(self, network_name, device_id, device_info):
        if network_name in self.mqtt_dict:
            return self.mqtt_dict[network_name].add_device(device_id, device_info)

    def check_status(self):
        status_dict = dict()
        for network_name in self.mqtt_dict:
            if self.mqtt_dict[network_name].isAlive():
                status_dict[network_name] = "run"
            else:
                status_dict[network_name] = "stop"
                logger.error("network(%s) is not alive, restart." % network_name)
                old_client = self.mqtt_dict[network_name]
                new_client = MqttClient(old_client.network_name, old_client.network_params, old_client.plugin_manager)
                del old_client
                self.mqtt_dict[network_name] = new_client
                self.mqtt_dict[network_name].start()
        return status_dict
