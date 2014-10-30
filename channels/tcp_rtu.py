#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
串口RTU通道类
通过调用管理类对象的process_data函数实现信息的发送。
"""

import logging

from pymodbus.client.sync import ModbusTcpClient

from libs.modbus_define import *
from libs.base_channel import BaseChannel


logger = logging.getLogger('yykj_serial')


class TcpRtuChannel(BaseChannel):
    def __init__(self, network, channel_name, channel_protocol, channel_params, manager, channel_type):
        self.server = channel_params.get("server", "")
        self.port = channel_params.get("port", "")
        self.modbus_client = None
        BaseChannel.__init__(self, network, channel_name, channel_protocol, channel_params, manager, channel_type)

    def run(self):
        self.modbus_client = ModbusTcpClient(host=self.server, port=self.port)
        try:
            self.modbus_client.connect()
            logger.debug("连接服务器成功.")
        except Exception, e:
            logger.error("连接服务器失败，错误信息：%r." % e)

    def isAlive(self):
        return True

    def send_cmd(self, device_info, device_cmd):
        if device_cmd["func_code"] == const.fc_read_coils or device_cmd["func_code"] == const.fc_read_discrete_inputs:
            req_result = self.modbus_client.read_coils(device_cmd["addr"],
                                                       device_cmd["count"],
                                                       unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": device_cmd["count"],
                "values": req_result.bits
            }

        elif device_cmd["func_code"] == const.fc_write_coil:
            req_result = self.modbus_client.write_coil(device_cmd["addr"],
                                                       device_cmd["value"],
                                                       unit=int(device_info["device_addr"]))
            res_result = self.modbus_client.read_coils(device_cmd["addr"],
                                                       1,
                                                       unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": 1,
                "values": req_result.bits[0:1]
            }
        elif device_cmd["func_code"] == const.fc_write_coils:
            req_result = self.modbus_client.write_coils(device_cmd["addr"],
                                                        device_cmd["values"],
                                                        unit=int(device_info["device_addr"]))
            counter = len(device_cmd["values"])
            res_result = self.modbus_client.read_coils(device_cmd["addr"],
                                                       counter,
                                                       unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": counter,
                "values": res_result.bits
            }
        elif device_cmd["func_code"] == const.fc_write_register:
            req_result = self.modbus_client.write_register(device_cmd["addr"],
                                                           device_cmd["value"],
                                                           unit=int(device_info["device_addr"]))
            res_result = self.modbus_client.read_holding_registers(device_cmd["addr"],
                                                                   1,
                                                                   unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": 1,
                "values": res_result.registers[0:1]
            }
        elif device_cmd["func_code"] == const.fc_write_registers:
            result = self.modbus_client.write_registers(device_cmd["addr"],
                                                        device_cmd["values"],
                                                        unit=int(device_info["device_addr"]))
            counter = len(device_cmd["values"])
            res_result = self.modbus_client.read_input_registers(device_cmd["addr"],
                                                                 counter,
                                                                 unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": counter,
                "values": res_result.registers
            }
        elif device_cmd["func_code"] == const.fc_read_holding_registers:
            res_result = self.modbus_client.read_holding_registers(device_cmd["addr"],
                                                                   device_cmd["count"],
                                                                   unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": device_cmd["count"],
                "values": res_result.registers
            }
        elif device_cmd["func_code"] == const.fc_read_input_registers:
            res_result = self.modbus_client.read_input_registers(device_cmd["addr"],
                                                                 device_cmd["count"],
                                                                 unit=int(device_info["device_addr"]))
            device_data = {
                "func_code": device_cmd["func_code"],
                "addr": device_cmd["addr"],
                "count": device_cmd["count"],
                "values": res_result.registers
            }
        else:
            logger.error("不支持的modbus指令：%d" % device_cmd["func_code"])
            device_data = None

        data_msg = {"device_info": device_info, "device_data": device_data}
        self.manager.process_data(self, self.network, self.name, self.protocol, data_msg)
