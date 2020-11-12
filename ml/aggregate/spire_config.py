# Addresses of machines uses to run a 6 machine (f=1,k=1) Spire configuration
# The IDS uses these to distinguish between known and unknown machines
# Edit this!

# The ML model labels all traffic from machines not listed as "other". If there are any machines that
# cause significant traffic in the system, they should be added here

ips = [
    # Scada master replicas
    '128.220.221.91',
    '128.220.221.92', 
    '128.220.221.93', 
    '128.220.221.94',
    '128.220.221.95', 
    '128.220.221.96',
    
    # Client (HMI/Proxy)
    '128.220.221.15',
    '128.220.221.16',
    '128.220.221.17'

    # Other machines should go here
]

macs = [
    # Scada master replicas
    '00:22:4d:b8:6f:04',
    '00:22:4d:b8:6f:a5',
    '00:22:4d:b7:64:32',
    '00:22:4d:b8:70:0c',
    '00:22:4d:d0:88:58',
    '00:22:4d:d0:88:74',

    # Client (HMI/Proxy)
    '00:22:4d:b5:86:75',
    '00:22:4d:b5:86:8b',
    '00:22:4d:b5:86:67'

    # Other machines should go here
]


# These sections are only used for calculating "flow features", e.g. the count of scada_master_ip -> client_ip packets
# These features are disabled by default
sm_ips = ips[:6]
client_ips = ips[6:9]
sm_macs = macs[:6]
client_macs = macs[6:9]
