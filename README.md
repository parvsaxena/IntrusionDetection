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
### Traffic Pattern based ML models
The traffic based model is based off the assumption that there is some pattern to the "normal" expected data, e.g. one minute
looks like another minute. So therefore the training data is grouped into "buckets" of a specified time period (defaults to one
minute). Each bucket simply stores the counts of different features, is a single data point for our model. Prediction then
consists of collecting a minute of real time packets, and feeding that bucket to our model.

The scripts in [`ml/aggregate`](ml/aggregate) are used to train such a model. Following is a brief descripttion of each files purpose
- `PacketAggregate.py`: Defines class for buckets and "intervals", which are groups of buckets
- `generate_aggregate.py`: Reads from database of parsed packets and generates "aggregate" object, which contains the buckets and other auxiliary info
- `featurize_aggregate.py`: Converts buckets to real vectors for training
- `train_aggregate.py`: Trains models
- `daemon.py`: Given a source of parsed packets, and a list of models, performs prediction. This consists of reading from the source, and once a bucket is completed, outputting the result from each model.

Note: `featurize_aggregate.py` is hardcoded to work with the specific spire config of 6 replicas, 1 machine for the HMI, and 1 for proxies. The ip and mac address need to be edited (though this will be changed so.

To create models, given there are parsed packets in the database, follow the steps below
```
python generate_aggregate.py
```
This will read from a default databse and output (by default) a file containing the aggregate called `baseline.out`. These and other parameters can be viewed by running the script with `--help`,
```
python featurize_aggregate.py
```
This will read from a given aggregate file (`baseline.out` by default) and output `aggregate_features.pkl` which is really just a matrix representation of the aggregate object, though any addresses not specified (see above) are instead labeled as "unknown". Again `--help` can be used to see various options.

```
python --algorithm lof
```
Trains a model, outputing it to a specified file (default `aggregate_model.py`). The algorithm should be specified as [`lof`](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html), [`svm`](https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html#sklearn.svm.OneClassSVM), or [`cov`](https://scikit-learn.org/stable/modules/generated/sklearn.covariance.EllipticEnvelope.html#sklearn.covariance.EllipticEnvelope).
Other options are also available to create different models.

Finally, make sure to put the models you wish to use in `modelPaths.py` in the prediction stage.


### Packet Analysis based ML models
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





