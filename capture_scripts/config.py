# Specifies models/other files that are used by the models
# All paths relative to the current folder

config = {
    "per_pkt": {
        # Model trained by per_packet scripts
        "model" : "./../ml/packet/lof_distinct_model.pkl",
        
        # The normalizer used to preprocess input, generated by featurize_per_pkt.py
        "scaler" : "./../ml/packet/lof_scaler.pkl",

        # Ouput log file
        "output": "per_pkt_output.log",
    },
    "aggregate": {
        # The training data generated by featurize_aggregate.py. Used to generate more a comparison to the 
        # "normal" traffic in the output 
        "training_data" : "./../ml/aggregate/features.pkl",

        # List of models (rather than a single one). Each time interval all will be used, and "vote" on a result
        # Ideally using multiple models with different algorithms/parameters decreases the false positive rate.
        "models" : [
             "./../ml/aggregate/model.pkl",
        ],

        # Output log file
        "output": "aggregate_output.log"
    }
}
