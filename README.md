## Pre-requisites:
- Python3.6 and above
- Scapy
- Postgresql

## Work flow:
1. Create database to store both raw and parsed packet data
2. Capture data for training and store in said database
3. Analyze, clean, and pre-process data
4. Offline training and tuning
5. Run in real time on current network traffic
6. Simulate attacks for testing

## 1. Database Setup:
Install postgres
```
sudo apt install postgresql postgresql-contrib
/etc/init.d/postgresql stop
/etc/init.d/postgresql start
```

Create database users
```
sudo -u postgres psql
sudo -u postgres createdb scada
create user mini;
grant all privileges on database scada to mini;
```

Create table
```
cd db_scripts; 
python3 createDB.py
```

Note: if previous tables already exist, then use `--recreate` option to drop and recreate tables.

## 2. Caputure Data

Capture traffic and insert into db(raw packets and parsed packets)

cd capture_scripts; sudo python train_live_capture.py &

Parameters in file:
- `Run_in_bg`
- `Is_training_mode` - set to True if just using for good data capture
- `Disable_db_insertion` - If set will not insert into db
- `iface` - give the SPAN port interface
- `timeout` - duration of traffic capture in seconds
- `filter` - Edit if we need to filter capture traffic at sniffing level

## 3. Explore Data
It is important to analyse the data captured. This will be helpful in feature engineering and parameter tuning

## 4. Training Models
### Traffic Pattern based ML modules

### Packet Analysis based ML modules
Extract from packet_feat table unique rows of needed data.

In psql -
```
Create table features as select ('ip_src', 'ip_dst', 'ip_ttl', 'ip_len', 'ip_ver', 'proto', 'mac_src', 'mac_dst',  'tcp_src_port', 'tcp_dst_port', 'udp_src_port', 'udp_dst_port', 'icmp_type', 'icmp_code', 'arp_op', 'arp_psrc', 'arp_pdst', 'arp_hwsrc', 'arp_hwdst', 'has_ip', 'has_ether', 'has_tcp', 'has_udp', 'has_icmp', 'has_arp') from packet_feats;

create table  sahiti_distinct as select distinct * from features;
```
This extracts distinct packets headers and make training faster.

Now run script -
```
cd ml;
check ips and mac addresses defined in init are correct.
python featurize_per_pkt.py (This is feature engineering step)
python lor_distinct_tr.py (This will generate the models)
```
Append the model and normalizer file paths to model_paths.py file in capture_scripts directory.

## 5. Real time prediction

```
cd capture_scripts;
sudo python test_capture_sahiti.py &
tail -f  perPkt_output.log  - This will print Traffic Pattern ML predictions
tail -f aggregate_output.log - This will print Packet Analysis based Ml predictions
```

## 6. Tests and attacks
```
cd dos_scripts
sudo python dos_attack_v2.py --help (This will print available choices of attack combos)
```

Some examples -

Replay attack

    sudo python dos_attack_v2.py --trans_proto UDP --source_ip scada1 --dest_ip mini2 --count 10

DoS attack

    sudo python dos_attack_v2.py --trans_proto UDP --dest_ip mini2/scada1 --count 10

Port Scanning

    sudo python dos_attack_v2.py --trans_proto TCP --count 10





