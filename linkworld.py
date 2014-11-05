#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    modbus网络的串口数据采集插件
    1、device_id的组成方式为ip_port_slaveid
    2、设备类型为0，协议类型为modbus
    3、devices_info_dict需要持久化设备信息，启动时加载，变化时写入
    4、device_cmd内容：json字符串
"""

import os
import sys
import time
import json
import logging

from libs.daemon import *
from libs.utils import cur_file_dir, convert
from libs.plugin_manager import PluginManager


# 全局变量
# 配置文件名称
config_file_name = "linkworld.cfg"

# 切换工作目录
# 程序运行路径
procedure_path = cur_file_dir()
# 工作目录修改为python脚本所在地址，后续成为守护进程后会被修改为'/'
os.chdir(procedure_path)

# 日志对象
logger = logging.getLogger('linkworld')
hdlr = logging.FileHandler('./linkworld.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def load_config(config_file_name):
    if os.path.exists(config_file_name):
        config_file = open(config_file_name, "r+")
        content = config_file.read()
        config_file.close()
        try:
            config_info = convert(json.loads(content.encode("utf-8")))
            logger.debug("load config info success，%s" % content)
            return config_info
        except Exception, e:
            logger.error("load config info fail，%r" % e)
            return None
    else:
        logger.error("config file is not exist. Please check!")
        return None


# 主函数
class LinkWorldDaemon(Daemon):
    def _run(self):
        # 初始化数据库
        # 加载设备数据
        plugin_params = load_config(config_file_name)
        if plugin_params is not None:
            plugin_manager = PluginManager()
            plugin_manager.load(plugin_params)
        else:
            logger.fatal("config_info is None. Please heck!")
            sys.exit(1)

        while True:
            logger.debug("system is running.")
            channel_status = plugin_manager.check_channel_status()
            logger.debug("channel_status:%r" % channel_status)
            mqtt_client_status = plugin_manager.check_mqtt_client_status()
            logger.debug("mqtt_client_status:%r" % mqtt_client_status)
            time.sleep(0.5)


# 主函数
def main(argv):
    daemon = LinkWorldDaemon('/tmp/plugin-daemon-linkworld.pid',
                             stdout="/tmp/gateway_plugin_linkworld.stdout",
                             stderr="/tmp/gateway_plugin_linkworld.stderr")

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            logger.info("Unknown command")
            sys.exit(2)
        sys.exit(0)
    elif len(sys.argv) == 1:
        daemon.run()
    else:
        logger.info("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()

