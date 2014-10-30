plugin_yykj_serial
==================

支持易运科技的硬件产品


关于配置项的说明：
[
    {
        "network_name": "network1", 
        "protocol": "", 
        "channels": [
            {
                "name": "tcpserver1", 
                "type": "tcp_server", 
                "params": {
                    "host": "127.0.0.1", 
                    "port": 10010
                }, 
                "preconfigured_devices": [
                    {
                        "device_type": "", 
                        "device_addr": "", 
                        "device_port": ""
                    }, 
                    {
                        "device_type": "", 
                        "device_addr": "", 
                        "device_port": "", 
                        "protocol": ""
                    }
                ]
            }, 
            {
                "name": "serial", 
                "type": "serial", 
                "params": {
                    "port": "/dev/ttyusb0", 
                    "baund": 9600
                }
            }
        ]
    }
]

具体运行时的设备情况存储在devices.txt中
protocol为协议类型名，同协议库文件名称，比如x*_y*.py对应的协议名为x*_y*
channel->type为通道类型，同通道库文件名称，比如x*_y*.py对应的通道类型为x*_y*

mqtt命令样例：
modbus_devices/1/0
{"command": {"count": 2, "addr": 0, "func_code": 3}}

yykj_devices/usr233/port1
{"command": "S01001"}
 
