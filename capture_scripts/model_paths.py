

model_paths = {
    "LORProcessor" : "./../ml/packet/lor_distinct_model.pkl",
    "scaler" : "./../ml/packet/lor_scaler.pkl",
    #"LORProcessor" : "./../ml/packet/lor_euc.pkl",
    #"scaler" : "./../ml/packet/scaler_euc.pkl",
    "perPkt_output": "./perPkt_output.log",
    "Agg_Baseline" : "./../ml/aggregate/baseline.out",
    "Agg_Featurized_Baseline" : "./../ml/aggregate/aggregate_features.pkl",
    "Agg_Model" : [
         "./../ml/aggregate/lof_nostd.pkl",
         "./../ml/aggregate/lof.pkl",
         "./../ml/aggregate/svm.pkl",
    ],
    "Agg_output": "./aggregate_output.log"
}
