from post_processing import (direct_merging, graph_merging,
                             graph_cleaning, coverage_cleaning,
                             direct_cleaning, cluster_and_neural_net)

analyse_methods = {
    "PWS": direct_cleaning,
    "PWM": direct_merging,
    "PGS": graph_cleaning,
    "PGM": graph_merging,
    "HCF": coverage_cleaning,
    "NNS": cluster_and_neural_net,
    "RAW": list
}
