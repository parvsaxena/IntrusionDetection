# Addresses of machines uses to run a 6 machine (f=1,k=1) Spire configuration
# The IDS uses these to distinguish between known and unknown machines
# Edit this!

ips = [
    '128.220.221.91',
    '128.220.221.92', 
    '128.220.221.93', 
    '128.220.221.94',
    '128.220.221.95', 
    '128.220.221.96',
    '128.220.221.15',
    '128.220.221.16',
    '128.220.221.17'
]
sm_ips = ips[:6]
client_ips = ips[6:]

macs = [
    '00:22:4d:b8:6f:04',
    '00:22:4d:b8:6f:a5',
    '00:22:4d:b7:64:32',
    '00:22:4d:b8:70:0c',
    '00:22:4d:d0:88:58',
    '00:22:4d:d0:88:74',
    '00:22:4d:b5:86:75',
    '00:22:4d:b5:86:8b',
    '00:22:4d:b5:86:67'
]
sm_macs = macs[:6]
client_macs = macs[6:]
