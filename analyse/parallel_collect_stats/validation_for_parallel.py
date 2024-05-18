import config
from analyse.parallel_collect_stats.data_class import RealTrackParams, CandTrackParams
from analyse.validation import get_characteristics
from selector import select_track_ids, select_track_ids_charged, select_track_ids_with_hits


def calc_parallel_characteristics(track_candidates,
                                  hit_list,
                                  trackId_to_track_params,
                                  event_number: int,
                                  min_length_proto=6,
                                  ratio=0.5,
                                  method=''):
    selected_trackIds = select_track_ids(trackId_to_track_params)

    # Get all lists of necessary data
    (reco_track_list, fake_track_list,
     duplicate_track_list, trackCandParamsList) = get_characteristics(selected_trackIds,
                                                                      track_candidates,
                                                                      hit_list,
                                                                      min_length_proto,
                                                                      ratio)

    # Remove short real track from recognized data
    reco_track_list = list(filter(lambda x: x in selected_trackIds, reco_track_list))

    # Calc mult
    selected_track_ids_ch = select_track_ids_charged(trackId_to_track_params)
    mult_ch = len(selected_track_ids_ch)

    selected_track_ids_h = select_track_ids_with_hits(trackId_to_track_params)
    mult_h = len(selected_track_ids_h)

    real_track_params = RealTrackParams(selected_trackIds=selected_trackIds,
                                        reco_track_list=reco_track_list,
                                        method=config.fname_real_tracks.format(method),
                                        trackId_to_track_params=trackId_to_track_params,
                                        mult_ch=mult_ch,
                                        mult_h=mult_h,
                                        event_number=event_number)

    cand_track_params = CandTrackParams(selected_trackIds=selected_trackIds,
                                        trackCandParamsList=trackCandParamsList,
                                        trackId_to_track_params=trackId_to_track_params,
                                        method=config.fname_track_candidates.format(method),
                                        mult_ch=mult_ch,
                                        mult_h=mult_h,
                                        event_number=event_number)

    return [real_track_params, cand_track_params]
