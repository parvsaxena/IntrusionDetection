# For all models/files/pickles that are referenced in analyzer.py or used by daemons it creates,
# Give paths to them, relative to the current folder

model_paths = {
    "LORProcessor" : "./../ml/packet/lor_distinct_model.pkl",
    "scaler" : "./../ml/packet/lor_scaler.pkl",
    #"LORProcessor" : "./../ml/packet/lor_euc.pkl",
    #"scaler" : "./../ml/packet/scaler_euc.pkl",
    "perPkt_output": "./perPkt_output.log",
    "Agg_Featurized_Baseline" : "./../ml/aggregate/features.pkl",
    "Agg_Model" : [
         "./../ml/aggregate/model.pkl",
    ],
    "Agg_output": "./aggregate_output.log"
}
