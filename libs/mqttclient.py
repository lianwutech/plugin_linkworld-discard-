#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
MQTT客户端类
内部有一个device_id和内部对象id的映射表和基于内部对象id的内部对象字典
"""
import json
import logging
import threading

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


logger = logging.getLogger('yykj_serial')


class MqttClient(threading.Thread):
    def __init__(self, network_name, network_params, plugin_manager):
        self.network_name = network_name
        self.plugin_manager = plugin_manager
        self.network_params = network_params
        self.protocol = network_params.get("protocol", "")
        mqtt_params = network_params.get("params", {})
        self.server_ip = mqtt_params.get("server", "127.0.0.1")
        self.server_port = mqtt_params.get("port", 1883)
        self.gateway_topic = mqtt_params.get("gateway_topic", "gateway")
        self.client_id = mqtt_params.get("client_id", network_name)
        # 加载params
        self.device_dict = dict()
        channels = network_params.get("channels", [])
        for channel in channels:
            channel_name = channel.get("name", "")
            preconfigured_devices = channel.get("preconfigured_devices", [])
            for device_info in preconfigured_devices:
                device_id = "%s/%s/%s" % (self.network_name,
                                          device_info.get("device_addr", ""),
                                          device_info.get("device_port"))
                device_info["device_id"] = device_id
                if "protocol" not in device_info:
                    device_info["protocol"] = self.protocol
                device_info["channel"] = channel_name
                self.device_dict[device_id] = device_info
                # 上报设备信息
                self.send_data(device_id, "")
        threading.Thread.__init__(self)

    def add_device(self, device_id, device_info):
        if device_id not in self.device_dict:
            logger.info("insert device(%s):%r" % (device_id, device_info))
            self.device_dict[device_id] = device_info
            # 上报设备信息
            self.send_data(device_id, "")
            return True
        else:
            logger.info("device(%s) is exist." % device_id)
            return False

    def run(self):
        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, rc):
            logger.info("Connected with result code " + str(rc))
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            try:
                mqtt_client.subscribe("%s/#" % self.network_name)
            except Exception, e:
                logger.error("subscribe fail.")

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            logger.info("收到数据消息" + msg.topic + " " + str(msg.payload))
            gateway_device_cmd = json.loads(msg.payload)["command"]
            device_id = msg.topic
            device_info = self.device_dict.get(device_id, None)
            if device_info is not None:
                device_cmd = self.plugin_manager.process_cmd(device_id, gateway_device_cmd)
                if device_cmd is not None:
                    retult = self.plugin_manager.send_cmd(device_id, device_cmd)
                    if retult:
                        logger.info("处理成功。")
                    else:
                        logger.error("处理失败。")
                else:
                    logger.error("plugin_manager.process_cmd fail。")

        mqtt_client = mqtt.Client(client_id=self.client_id)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        try:
            mqtt_client.connect(self.server_ip, self.server_port, 60)
            mqtt_client.loop_forever()
        except Exception, e:
            logger.error("MQTT链接失败，错误内容:%r" % e)
            # 关闭并删除mqtt连接，为重新起新线程做准备
            mqtt_client.disconnect()
            mqtt_client = None

    def send_data(self, device_id, device_data):
        if device_id in self.device_dict:
            device_info = self.device_dict[device_id]
            if device_data is None:
                # 空数据以空字符串的形式传递，网关将丢弃该消息
                device_data = ""
            # 组包
            device_msg = {
                "device_id": device_id,
                "device_type": device_info["device_type"],
                "device_addr": device_info["device_addr"],
                "device_port": device_info["device_port"],
                "protocol": device_info["protocol"],
                "data": device_data
            }

            # MQTT发布
            try:
                publish.single(topic=self.gateway_topic,
                               payload=json.dumps(device_msg),
                               hostname=self.server_ip,
                               port=self.server_port)
                logger.info("send_data:向Topic(%s)发布消息：%s" % (self.gateway_topic, device_msg))
                return True
            except Exception, e:
                logger.error("send_data:向Topic(%s)发布消息：%s，发送失败，失败内容：%r" % (self.gateway_topic, device_msg, e))
                return False
        else:
            logger.error("device(%s) is not exist in network(%s)." % (device_id, self.network_name))
            return False

