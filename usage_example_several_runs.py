from post_processing import (direct_merging, graph_merging,
                             graph_cleaning, coverage_cleaning,
                             direct_cleaning, create_model,
                             cluster_and_neural_net)
import config
import save_to_files
import datetime
import psutil

from analyse.validation import calc_characteristics, calc_mult
from analyse.visualizing import MainWindow
from data_processing.parse_data import *
from PyQt6.QtWidgets import QApplication
from copy import deepcopy
import pandas as pd
import sys
import os

#if os.path.exists(config.fname_real_tracks):
#  os.remove(config.fname_real_tracks)
#  save_to_files.write_real_tracks_header(config.fname_real_tracks)


def find_file(f_name, dir_list):
    full_f_name = ""
    for dir in dir_list:
        full_f_name_local = os.path.join(dir, f_name)
        if os.path.exists(full_f_name_local):
            full_f_name = full_f_name_local
            break
    if full_f_name == "":
        print(f"Warning: find_file(): can not find {f_name}")
    return full_f_name


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

    for method in methods:
        fname = config.fname_real_tracks.format(method)
        if os.path.exists(fname):
            os.remove(fname)
        save_to_files.write_real_tracks_header(fname)

        fname = config.fname_track_candidates.format(method)
        if os.path.exists(fname):
            os.remove(fname)
        save_to_files.write_track_candidates_header(fname)

#   dirs = ['data/tracks_data']
    dirs = [
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/0_1000',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/1000_1800',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/1801_2989',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/2991_4185',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/4186_4364',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/4367_4999',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/5000_5202',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/5204_6203',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/6204_7203',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/7204_8103',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/8104_8184',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/8185_9184',
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/9185_9999'
    ]
#   track_candidates_params_fname = "data/data_for_ml/track_candidates_params.csv"
    dirs_param = [
            '/media/space/pbelecky/hep/mpdroot_bak/dump_pt_eta_2_10000/track_candidates_params'
    ]
    dirs_mc = [
            '/home/belecky/work/mpdroot/bin_dump_pdg/macros/common'
    ]

    d = int((config.end_event - config.start_event + 1) / config.n_parts)

    i_part = int(sys.argv[1])
    start_event_i = config.start_event + d * i_part
    end_event_i   = config.start_event + d *(i_part + 1) - 1
    out_file_postfix = i_part

    print(f"i: {i_part}, start_event_i: {start_event_i}, "
          f" end_event_i: {end_event_i}")

    # Upload data and settings for NNS (Can be commented out if you don't use NNS)
    model = create_model()
    model.load_weights('data/data_for_ml/checkpoint_dir/cp.ckpt')

    for iEvent in range(config.start_event, config.end_event + 1):
        print(f"Event #{iEvent}")

        prototracks_fname = find_file(f"event_{iEvent}_prototracks.txt", dirs)
        space_points_fname = find_file(f"event_{iEvent}_space_points.txt", dirs)
        mc_track_params_fname = find_file(f"event_{iEvent}_mc_track_params.txt", dirs_mc)
        track_candidates_params = find_file(f"event_{iEvent}_track_candidates_params.txt", dirs_param)

        if (prototracks_fname       == "") or \
           (space_points_fname      == "") or \
           (mc_track_params_fname   == "") or \
           (track_candidates_params == ""):
            continue

        # Upload data
        data_from_get_tracks_data = get_tracks_data(prototracks_fname,
                                                    space_points_fname)

        result = {"RAW": get_tracks_data(prototracks_fname, space_points_fname)}

        # Strange Check prototracks file not empty
#       if not result.get("RAW"):
#           print(f"WARNING: post_process(): iEvent: {iEvent}: no input prototracks")
#           continue
        hit_list = get_hits(space_points_fname)
        trackId_to_track_params = get_trackId_to_track_params(
                mc_track_params_fname)

        mult_ch_pri = calc_mult(trackId_to_track_params,   # multiplicity by Val Kuz
                only_pri=True, with_hits=False, charged=True, debug=False)
        print(f"event_number: {iEvent}; mult_ch_pri(Val) = {mult_ch_pri}")

        trackId_to_hits_dict = get_trackId_to_hits_dict(
                space_points_fname, trackId_to_track_params)


        df = pd.read_csv(track_candidates_params)
        indices = df['prototrackIndex']
#       df = df.iloc[:, 1:-2]
        df = df.iloc[:, 2:-2]

        # Use methods
        if df.size == 0:
            result["NNS"] = [[]]
        else:
            result["NNS"] = cluster_and_neural_net(model, deepcopy(result.get("RAW")), df,
                                                   pd.Series([iEvent] * len(df)), indices, hits=3)

        result["PWS"] = direct_cleaning(deepcopy(result.get("RAW")))
        result["PWM"] = direct_merging(deepcopy(result.get("RAW")))
        result["PGS"] = graph_merging(deepcopy(result.get("RAW")))
        result["PGM"] = graph_cleaning(deepcopy(result.get("RAW")))
        result["HCF"] = coverage_cleaning(deepcopy(result.get("RAW")))

        # Computation efficiency
        for post_processing_method, result_data in result.items():
            characteristic_dict = calc_characteristics(result_data, hit_list, trackId_to_hits_dict, trackId_to_track_params,
                method=post_processing_method,
                mult=mult_ch_pri)

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
    post_process()
    if (config.visualyse):
      app = QApplication(sys.argv)
      plot = MainWindow(list(result.values()), trackId_to_hits_dict)
      plot.show()
      sys.exit(app.exec())
