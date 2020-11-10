# For all models/files/pickles that are referenced in analyzer.py or used by daemons it creates,
# Give paths to them, relative to the current folder

config = {
    "per_pkt": {
        "model" : "./../ml/packet/lof_distinct_model.pkl",
        "scaler" : "./../ml/packet/lof_scaler.pkl",
        "output": "./per_pkt_output.log",
    },
    "aggregate": {
        "training_data" : "./../ml/aggregate/features.pkl",
        "models" : [
             "./../ml/aggregate/model.pkl",
        ],
        "output": "./aggregate_output.log"
    }
}
