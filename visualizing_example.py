from analyse.parallel_collect_stats.utils import load_csv
from post_processing import (direct_merging, graph_merging,
                             graph_cleaning, coverage_cleaning,
                             direct_cleaning, create_model,
                             cluster_and_neural_net)
from analyse.visualizing import MainWindow
from data_processing.parse_data import *
from PyQt6.QtWidgets import QApplication
from copy import deepcopy
import sys

result = {"RAW": get_tracks_data("data/tracks_data/event_0_prototracks.txt",
                                 "data/tracks_data/event_0_space_points.txt")}

hit_list = get_hits("data/tracks_data/event_0_space_points.txt")
trackId_to_track_params = get_trackId_to_track_params("data/tracks_data/event_0_mc_track_params.txt")
trackId_to_hits_dict = get_trackId_to_hits_dict("data/tracks_data/event_0_space_points.txt", trackId_to_track_params)

# Upload data and settings for NNS (Can be commented out if you don't use NNS)
model = create_model()
model.load_weights('post_processing/cleaning/tf_neural_net/weight_data/cp.ckpt')
df = load_csv('data/tracks_data/event_0_track_candidates_params.txt')

indices = df['prototrackIndex']
event_num = df['#format:eventNumber']
df = df.iloc[:, 2:-2]

# Use methods
result["NNS"] = cluster_and_neural_net(model, deepcopy(result.get("RAW")), df, event_num, indices, hits=3)
result["PWS"] = direct_cleaning(deepcopy(result.get("RAW")))
result["PWM"] = direct_merging(deepcopy(result.get("RAW")))
result["PGS"] = graph_cleaning(deepcopy(result.get("RAW")))
result["PGM"] = graph_merging(deepcopy(result.get("RAW")))
result["HCF"] = coverage_cleaning(deepcopy(result.get("RAW")))

# Computation efficiency
for post_processing_method, result_data in result.items():
    # Remove hit indexes for visualizing
    if len(result_data[0][0]) > 3:
        for track_id in range(len(result_data)):
            for hit_id in range(len(result_data[track_id])):
                result_data[track_id][hit_id] = result_data[track_id][hit_id][1:]

# Start visualizing
if __name__ == '__main__':
    app = QApplication(sys.argv)
    plot = MainWindow(list(result.values()), trackId_to_hits_dict)
    plot.show()
    sys.exit(app.exec())
