#TODO: find scada3 ip

machines = {
"scada1": {'ip':'128.220.221.91', 'mac':'00:22:4d:b8:6f:04', 'port':4546},
"scada2": {'ip':'128.220.221.92', 'mac':'00:22:4d:b8:6f:a5', 'port':4546},
"scada3": {'ip':'128.220.221.93', 'mac':'', 'port':'4546'},
"scada4": {'ip':'128.220.221.94', 'mac':'00:22:4d:b8:70:0c', 'port':4546},
"scada5": {'ip':'128.220.221.95', 'mac':'00:22:4d:d0:88:58', 'port':4546},
"scada6": {'ip':'128.220.221.96', 'mac':'00:22:4d:d0:88:74', 'port':4546},
"mini1": {'ip':'128.220.221.15', 'mac':'00:22:4d:b5:86:75', 'port':4546},
"mini2": {'ip':'128.220.221.16', 'mac':'00:22:4d:b5:86:8b', 'port':4546},
"mini3": {'ip':'128.220.221.17', 'mac':'00:22:4d:b5:86:67', 'port':4546},
}


qeury_machines = "SELECT DISTINCT mac_src, ip_src FROM packet_feat where has_arp=False;"
