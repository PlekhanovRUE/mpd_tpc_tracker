import os

from config import SettingParams
from analyse.parallel_collect_stats.data_class import (InputEventData, TrackData,
                                                       MlModelData, OneEventRealTrackParams)
from analyse.parallel_collect_stats.validation_for_parallel import calc_parallel_characteristics
from data_processing.parse_data import get_tracks_data, get_hits, get_trackId_to_track_params
from analyse.parallel_collect_stats.static_data import analyse_methods
from save_to_files import write_real_tracks_header, write_track_candidates_header


def parse_event_data(event_number: int, input_dir: str) -> InputEventData:
    proto_tracks_fname = f"{input_dir}/event_{event_number}_prototracks.txt"
    sp_points_fname = f"{input_dir}/event_{event_number}_space_points.txt"
    mc_track_params_fname = f"{input_dir}/event_{event_number}_mc_track_params.txt"

    input_event_data = InputEventData(
        hits_list=get_hits(sp_points_fname),
        track_id_to_track_params=get_trackId_to_track_params(mc_track_params_fname)
    )
    input_event_data.tracks = get_tracks_data(proto_tracks_fname, sp_points_fname)

    return input_event_data


def nns_analyse(event_number: int,
                ml_data: MlModelData,
                event_data: InputEventData,
                nn_method,
                input_dir: str) -> list[TrackData]:
    ml_data.calc_event_filed(event_number, input_dir)

    # Skip empty events
    if ml_data.event_df.size == 0:
        return [[]]

    return nn_method(model=ml_data.model,
                     track_list=event_data.tracks,
                     tracks_for_nn=ml_data.event_df,
                     event_number=ml_data.event_num_ser,
                     indices=ml_data.indices)


def calculate_one_event_stats(event_number: int, input_dir: str, ml_data: MlModelData) -> OneEventRealTrackParams:
    event_data = parse_event_data(event_number, input_dir)
    event_characteristics = OneEventRealTrackParams()

    for method_name, method in analyse_methods.items():
        match method_name:
            case "NNS":
                tracks = nns_analyse(event_number, ml_data, event_data, method, input_dir)
            case "RAW":
                tracks = event_data.tracks
            case _:
                tracks = method(tracks=event_data.tracks)
        # Calc characteristics for real and cand tracks
        (real_tracks_param, cand_tracks_param) = calc_parallel_characteristics(tracks,
                                                                               event_data.hits_list,
                                                                               event_data.track_id_to_track_params,
                                                                               method=method_name,
                                                                               event_number=event_number)
        event_characteristics.all_method_for_real_tracks.append(real_tracks_param)
        event_characteristics.all_method_for_cand_tracks.append(cand_tracks_param)
    return event_characteristics


def rewrite_stats_files():
    for method in analyse_methods.keys():
        fname = SettingParams.fname_real_tracks.format(method)
        if os.path.exists(fname):
            os.remove(fname)
        write_real_tracks_header(fname)

        fname = SettingParams.fname_track_candidates.format(method)
        if os.path.exists(fname):
            os.remove(fname)
        write_track_candidates_header(fname)
