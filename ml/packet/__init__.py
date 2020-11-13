"""
If not NN , we need to transform feature vector to be numerical, so below map known/correct IPs, macs, ports.
They will be used by transform function to do feature engineering.
"""

machines = {
    #Scada Masters
    '128.220.221.91': ['00:22:4d:b8:6f:04', 4546],
    '128.220.221.92': ['00:22:4d:b8:6f:a5', 4546],
    '128.220.221.93': ['00:00:00:00:00:00', 4546],
    '128.220.221.94': ['00:22:4d:b8:70:0c', 4546],
    '128.220.221.95': ['00:22:4d:d0:88:58', 4546],
    '128.220.221.96': ['00:22:4d:d0:88:74', 4546],
    #Minis- plcs, hmis
    '128.220.221.15': ['00:22:4d:b5:86:75', 4546],
    '128.220.221.16': ['00:22:4d:b5:86:8b', 4546],
    '128.220.221.17': ['00:22:4d:b5:86:67', 4546],
}
macs = [
    #Macs of above machines
    '00:22:4d:b8:6f:04',
    '00:22:4d:b8:6f:a5', 
    '00:00:00:00:00:00', 
    '00:22:4d:b8:70:0c', 
    '00:22:4d:d0:88:58',
    '00:22:4d:d0:88:74', 
    '00:22:4d:b5:86:8b', 
    '00:22:4d:b5:86:67', 
    '28:c0:da:7a:7f:81',
]
ports=[
    #Ports that are authorized to operate
    4546,
    53,
    34489,
    5353,
    68,123,
    34835
]
#maps IPs to known and unknown set
def do_ip(ip):
    val=1
    if ip in machines.keys():
        val=100
    return val

#maps MACs to known and unknown set
def do_mac(ip,mac):
    val=1
    if ip in machines.keys():
        if mac==machines[ip][0]:
            val=100
        else:
            val=-100
    return val

def do_only_mac(mac):
    val=1
    if mac in macs:
        val=100
    return val

#maps Ports to known and unknown set
def do_ports(port):
    val=1
    if port in ports:
        val=100
    return val

#Header features are transformed into vectors used for training
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
            if field in ['udp_src_port','udp_dst_port']:
                value=do_ports(row[field])
        """
        if field in ['has_ip','has_ether','has_tcp','has_udp','has_icmp','has_arp']:
            if value==-5:
                value=0
        """        
        vec[field]=value
        

        # print("{}, {}: {} , {}".format(index,field,row[field],vec[field]))
        # print(vec)
    return vec

#features selected after feature engineering. If we want to add or delete the field from feature vector we need to change this
#distinct_cols=['ip_src', 'ip_dst', 'ip_ttl', 'ip_len', 'ip_ver', 'proto', 'mac_src', 'mac_dst', 'ether_type', 'tcp_src_port', 'tcp_dst_port', 'udp_src_port', 'udp_dst_port', 'udp_len', 'icmp_type', 'icmp_code', 'arp_op', 'arp_psrc', 'arp_pdst', 'arp_hwsrc', 'arp_hwdst', 'has_ip', 'has_ether', 'has_tcp', 'has_udp', 'has_icmp', 'has_arp']
distinct_cols=['ip_src', 'ip_dst', 'ip_ttl', 'ip_len', 'ip_ver', 'proto', 'mac_src', 'mac_dst',  'tcp_src_port', 'tcp_dst_port', 'udp_src_port', 'udp_dst_port', 'icmp_type', 'icmp_code', 'arp_op', 'arp_psrc', 'arp_pdst', 'arp_hwsrc', 'arp_hwdst', 'has_ip', 'has_ether', 'has_tcp', 'has_udp', 'has_icmp', 'has_arp']
