machines = {
'128.220.221.91': ['00:22:4d:b8:6f:04', 4546],
'128.220.221.92': ['00:22:4d:b8:6f:a5', 4546],
'128.220.221.93': ['00:00:00:00:00:00', 4546],
'128.220.221.94': ['00:22:4d:b8:70:0c', 4546],
'128.220.221.95': ['00:22:4d:d0:88:58', 4546],
'128.220.221.96': ['00:22:4d:d0:88:74', 4546],
'128.220.221.15': ['00:22:4d:b5:86:75', 4546],
'128.220.221.16': ['00:22:4d:b5:86:8b', 4546],
'128.220.221.17': ['00:22:4d:b5:86:67', 4546],
'128.220.221.1' : ['28:c0:da:7a:7f:81',0],
'128.220.221.2' : ['d4:ae:52:c6:c2:34',0],
'224.0.0.251'   : ['01:00:5e:00:00:fb',0],
'255.255.255.255':['ff:ff:ff:ff:ff:ff',0],
'128.220.221.5' : ['00:1c:73:0b:21:83',0],
'169.254.10.173': ['00:22:4d:b5:87:f1',0],
'0.0.0.0'       : ['58:97:1e:e0:d0:c0',0],
'169.254.100.100': ['c4:04:15:b0:83:2c',0]
}
macs = [
'00:22:4d:b8:6f:04',
'00:22:4d:b8:6f:a5', 
'00:00:00:00:00:00', 
'00:22:4d:b8:70:0c', 
'00:22:4d:d0:88:58',
'00:22:4d:d0:88:74', 
'00:22:4d:b5:86:8b', 
'00:22:4d:b5:86:67', 
'28:c0:da:7a:7f:81',
'd4:ae:52:c6:c2:34',
'01:00:5e:00:00:fb',
'00:22:4d:b5:86:75',
'ff:ff:ff:ff:ff:ff'
]

def do_ip(ip):
    val=10
    if ip in machines.keys():
        val=100
    return val

def do_mac(ip,mac):
    val=10
    if ip in machines.keys():
        if mac==machines[ip][0]:
            val=100
        else:
            val=-100
    return val

def do_only_mac(mac):
    val=10
    if mac in macs:
        val=100
    return val

def transform(row,fields):
    #print
    vec={}
     
    for field in fields.values():
        if field not in row.keys():
            row[field]=0
    
    for index,field in fields.items():
        value=row.get(field)
        if value is None:
            value=0
        if type(value) == type(True):
            value=int(value) * 100
        if type(value) == type(False):
            value=int(value)
        
        if value!=0:
            if field=='ip_src':
                value=do_ip(row[field])
            if field=='ip_dst':
                value=do_ip(row[field])
            if field=='mac_src':
                #value=do_only_mac(row[field])
                
                if  row.get('has_arp')==bool(1):
                    value=do_mac(row['arp_psrc'],row[field])
                    #value=do_only_mac(row[field])
                else:
                    value=do_mac(row.get('ip_src',-5),row[field])
                
            if field=='mac_dst':
                
                if  row.get('has_arp')==bool(1):
                    value=do_mac(row['arp_pdst'],row[field])
                    #value=do_only_mac(row[field])
                else:
                    value=do_mac(row.get('ip_dst',-5),row[field])
                    
                #value=do_only_mac(row[field])
            if field=='arp_psrc':
                value=do_ip(row[field])
            if field=='arp_pdst':
                value=do_ip(row[field])
            if field=='arp_hwsrc':
                value=do_mac(row['arp_psrc'],row[field])
            if field=='arp_hwdst':
                value=do_mac(row['arp_pdst'],row[field])
        """
        if field in ['has_ip','has_ether','has_tcp','has_udp','has_icmp','has_arp']:
            if value==-5:
                value=0
        """        
        vec[field]=value
        

        # print("{}, {}: {} , {}".format(index,field,row[field],vec[field]))
        # print(vec)
    return vec

#distinct_cols=['ip_src', 'ip_dst', 'ip_ttl', 'ip_len', 'ip_ver', 'proto', 'mac_src', 'mac_dst', 'ether_type', 'tcp_src_port', 'tcp_dst_port', 'udp_src_port', 'udp_dst_port', 'udp_len', 'icmp_type', 'icmp_code', 'arp_op', 'arp_psrc', 'arp_pdst', 'arp_hwsrc', 'arp_hwdst', 'has_ip', 'has_ether', 'has_tcp', 'has_udp', 'has_icmp', 'has_arp']
distinct_cols=['ip_src', 'ip_dst', 'ip_ttl', 'ip_len', 'ip_ver', 'proto', 'mac_src', 'mac_dst', 'ether_type', 'tcp_src_port', 'tcp_dst_port', 'udp_src_port', 'udp_dst_port', 'icmp_type', 'icmp_code', 'arp_op', 'arp_psrc', 'arp_pdst', 'arp_hwsrc', 'arp_hwdst', 'has_ip', 'has_ether', 'has_tcp', 'has_udp', 'has_icmp', 'has_arp']
