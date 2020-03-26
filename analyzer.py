from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP

# Time ??, Source IP(d), Destination IP(d), Protocol ??, Length(d),
# Source Port(d), Dest Port(d), TTL(d), IP version ??
# https://www.howtoinstall.co/en/ubuntu/xenial/tshark

def parse_packet(pkt_data):
    ip_pkt = IP(pkt_data)
    dict = {}
    # print(type(ip_pkt))
    if ip_pkt is not None:
        # print(ip_pkt.show())
        dict['ip_src'] = ip_pkt.src
        dict['ip_dst'] = ip_pkt.dst
        # TODO: fix ttl
        dict['ip_ttl'] = ip_pkt.ttl
        dict['ip_len'] = ip_pkt.len
        # TODO: version seems off
        dict['ip_ver'] = ip_pkt.version
    else:
        dict['ip_src'] = None
        dict['ip_dst'] = None
        dict['ip_ttl'] = None
        dict['ip_len'] = None
        dict['ip_ver'] = None

    dll_pkt = TCP(pkt_data)
    if dll_pkt is not None:
        # print("TCP dump")
        # print(dll_pkt.show())
        dict['dll_port'] = 'tcp'
        dict['src_port'] = dll_pkt.sport
        dict['dst_port'] = dll_pkt.dport
    else:
        dll_pkt = UDP(pkt_data)
        if dll_pkt is not None:
            # print("UPD dump")
            # print(dll_pkt.show())
            dict['dll_port'] = 'udp'
            dict['src_port'] = dll_pkt.sport
            dict['dst_port'] = dll_pkt.dport
        else:
            # print("Nothing here")
            dict['dll_port'] = None
            dict['src_port'] = None
            dict['dst_port'] = None

    #TODO: Figure out why this doesn't work with live_capture
    # Maybe because the captured live data there is already l2.Ether, while RawCapReader returns bytes

    # ether_pkt = Ether(pkt_data)
    #
    # if ether_pkt is not None:
    #     dict['mac_src'] = ether_pkt.src
    #     dict['mac_dst'] = ether_pkt.dst
    #     print(ether_pkt.show())
    # else:
    #     dict['mac_src'] = None
    #     dict['mac_dst'] = None

    print("\nDictionary\n", dict)
    return


count = 0


if __name__ == "__main__":
    for pkt_data, pkt_metadata in RawPcapReader('example.pcap'):
        count = count + 1
        print("Packet no ", count)
        # print(pkt_metadata)
        # print(pkt_data)
        print(type(pkt_data))
        parse_packet(pkt_data)
