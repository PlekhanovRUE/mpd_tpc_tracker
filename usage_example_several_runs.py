import torch

from post_processing import (direct_merging, graph_merging,
                             graph_cleaning, coverage_cleaning,
                             direct_cleaning, FCNeuralNet,
                             cluster_and_neural_net)
import config
import save_to_files
import datetime
import psutil
from selector import select_track_ids_charged, select_track_ids_with_hits

from analyse.validation import calc_characteristics, calc_mult
from analyse.visualizing import MainWindow
from data_processing.parse_data import *
from PyQt6.QtWidgets import QApplication
from copy import deepcopy
import pandas as pd
import sys
import os
import uuid


def check_file(fname):
    if not os.path.exists(fname):
        print(f"Warning: can not find {fname}!")
        return False
    return True


def check_params():
    i_thread = int(sys.argv[1])
    n_threads = config.n_parts
    if (i_thread >= n_threads):
        print(f"Error: bad parameters: " \
              f"total number of threads: {n_threads}\n" \
              f"i_thread actual: {i_thread}\n" \
              f"i_thread expected: [0, {n_threads - 1}]")
        return False
    return True


def load_csv(fname):
    # Open input params file
    with open(fname) as f:
        content = f.read()

    # Change separator
    content = content.replace(" ", "")

    # Save uniq_fname file with correct sep
    uniq_fname = "/tmp/" + str(uuid.uuid4().hex)
    with open(uniq_fname, "w") as f:
        f.write(content)

    df = pd.read_csv(uniq_fname)

    # Delete temp file
    os.remove(uniq_fname)

    return df

def post_process():
    methods = [
      "RAW",
      "NNS",
      "PWS",
      "PWM",
      "PGS",
      "PGM",
      "HCF"
    ]

    input_dir = 'data/tracks_data'

    d = int((config.end_event - config.start_event + 1) / config.n_parts)

    i_part = int(sys.argv[1])
    start_event_i = config.start_event + d * i_part
    end_event_i   = config.start_event + d *(i_part + 1) - 1
    out_file_postfix = i_part

    print(f"i: {i_part}, start_event_i: {start_event_i}, "
          f" end_event_i: {end_event_i}")

    for method in methods:
        fname = config.fname_real_tracks.format(method, out_file_postfix)
        if os.path.exists(fname):
            os.remove(fname)
        save_to_files.write_real_tracks_header(fname)

        fname = config.fname_track_candidates.format(method, out_file_postfix)
        if os.path.exists(fname):
            os.remove(fname)
        save_to_files.write_track_candidates_header(fname)

    # Upload data and settings for NNS (Can be commented out if you don't use NNS)
    model = FCNeuralNet()
    model.load_state_dict(torch.load("post_processing/cleaning/pytorch_neural_net/weight_best.pth",
                                     map_location=torch.device("cpu")))
    model.eval()

    for iEvent in range(start_event_i, end_event_i + 1):
        print(f"Event #{iEvent}")

        prototracks_fname = f"{input_dir}{os.sep}event_{iEvent}_prototracks.txt"
        track_cand_params_fname = f"{input_dir}{os.sep}event_{iEvent}_" \
                "track_candidates_params.txt"
        sp_points_fname = f"{input_dir}{os.sep}event_{iEvent}_space_points.txt"
        mc_track_params_fname = f"{input_dir}{os.sep}event_{iEvent}_" \
                "mc_track_params.txt"

        inp_files_exists = check_file(prototracks_fname) and \
                           check_file(track_cand_params_fname) and \
                           check_file(sp_points_fname) and \
                           check_file(mc_track_params_fname)
        if not inp_files_exists:
            continue

        # Upload data
        data_from_get_tracks_data = get_tracks_data(prototracks_fname,
                                                    sp_points_fname)

        result = {"RAW": get_tracks_data(prototracks_fname, sp_points_fname)}

        # Strange Check prototracks file not empty
#       if not result.get("RAW"):
#           print(f"WARNING: post_process(): iEvent: {iEvent}: no input prototracks")
#           continue
        hit_list = get_hits(sp_points_fname)
        trackId_to_track_params = get_trackId_to_track_params(
                mc_track_params_fname)

        selected_track_ids_ch = select_track_ids_charged(trackId_to_track_params)
        mult_ch = len(selected_track_ids_ch)
        print("multiplicity ch: {}".format(mult_ch))

        selected_track_ids_h = select_track_ids_with_hits(trackId_to_track_params)
        mult_h = len(selected_track_ids_h)
        print("multiplicity h: {}".format(mult_h))

        trackId_to_hits_dict = get_trackId_to_hits_dict(
                sp_points_fname, trackId_to_track_params)

        nn_data = load_csv(track_cand_params_fname)
        df = nn_data[nn_data['#format:eventNumber'] == iEvent].reset_index(drop=True)
        df = df.iloc[:, 2:-2]

        # Use methods
        if df.size == 0:
            result["NNS"] = [[]]
        else:
            result["NNS"] = cluster_and_neural_net(deepcopy(result.get("RAW")), df, model)

        result["PWS"] = direct_cleaning(deepcopy(result.get("RAW")))
        result["PWM"] = direct_merging(deepcopy(result.get("RAW")))
        result["PGS"] = graph_merging(deepcopy(result.get("RAW")))
        result["PGM"] = graph_cleaning(deepcopy(result.get("RAW")))
        result["HCF"] = coverage_cleaning(deepcopy(result.get("RAW")))

        # Computation efficiency
        for post_processing_method, result_data in result.items():
            characteristic_dict = calc_characteristics(result_data, hit_list, trackId_to_hits_dict, trackId_to_track_params,
                method=post_processing_method,
                mult_ch=mult_ch,
                mult_h=mult_h,
                out_file_postfix=out_file_postfix,
                event_number=iEvent)

            print(f"\n\n################## {post_processing_method} ##################")

            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{time} event #{iEvent}")

            process = psutil.Process()
            mem = round(process.memory_info().rss / (1024**2)) # bytes to Mb
            print(f"memory: {mem} Mb")

            for characteristic, value in characteristic_dict.items():
                print(f"{characteristic}: {value}")

            if (config.visualyse):
              # Remove hit indexes for visualizing
              if len(result_data[0][0]) > 3:
                  for track_id in range(len(result_data)):
                      for hit_id in range(len(result_data[track_id])):
                          result_data[track_id][hit_id] = result_data[track_id][hit_id][1:]
            try:
              result_data[0][0]
            except:
              print(f"Error: event {iEvent} cannot get result_data[0][0]")

# Start visualizing
if __name__ == '__main__':
    if not check_params():
      sys.exit()
    post_process()
    if (config.visualyse):
      app = QApplication(sys.argv)
      plot = MainWindow(list(result.values()), trackId_to_hits_dict)
      plot.show()
      sys.exit(app.exec())
