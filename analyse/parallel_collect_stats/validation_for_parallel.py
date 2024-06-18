from config import SettingParams
from analyse.parallel_collect_stats.data_class import RealTrackParams, CandTrackParams
from selector import select_track_ids, select_track_ids_charged, select_track_ids_with_hits


def calc_parallel_characteristics(track_candidates,
                                  hit_list,
                                  trackId_to_track_params,
                                  event_number: int,
                                  min_length_proto=SettingParams.n_proto_hits_min,
                                  ratio=SettingParams.ratio,
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
                                        method=SettingParams.fname_real_tracks.format(method),
                                        trackId_to_track_params=trackId_to_track_params,
                                        mult_ch=mult_ch,
                                        mult_h=mult_h,
                                        event_number=event_number)

    cand_track_params = CandTrackParams(selected_trackIds=selected_trackIds,
                                        trackCandParamsList=trackCandParamsList,
                                        trackId_to_track_params=trackId_to_track_params,
                                        method=SettingParams.fname_track_candidates.format(method),
                                        mult_ch=mult_ch,
                                        mult_h=mult_h,
                                        event_number=event_number)

    return [real_track_params, cand_track_params]


def replace_hits_to_track_id(tracks, hits):
    tracks_hits = []
    for i in range(len(tracks)):
        tracks_hits.append([])
        for hit in tracks[i]:
            hit_id = int(hit[0])
            truth_track_id = int(hits[hit_id][3])
            tracks_hits[i].append(truth_track_id)
    return tracks_hits


class TrackCandParams:
    selected = None
    isDup = None
    trackId = None
    isFake = None
    nHits = None


def get_characteristics(selected_trackIds, track_candidates, hits, n, ratio):
    reco_tracks = set()
    fake_tracks = set()
    duplicate_tracks = []

    trackCandParamsList = []
    for _ in track_candidates:
        params = TrackCandParams()
        trackCandParamsList.append(params)

    # Replace hits in track with id of their real track
    tracks_hits = replace_hits_to_track_id(track_candidates, hits)
    for i in range(len(track_candidates)):

        lenTrackCand = len(track_candidates[i])

        trackCandParamsList[i].nHits = lenTrackCand

        if lenTrackCand < n:
            trackCandParamsList[i].selected = False
            trackCandParamsList[i].isDup = None
            trackCandParamsList[i].trackId = None
            trackCandParamsList[i].isFake = None
            continue

        # Find the most common real track id in reco track
        reco_track_id = max(tracks_hits[i], key=tracks_hits[i].count)

        selected = reco_track_id in selected_trackIds

        curRatio = tracks_hits[i].count(reco_track_id) / len(tracks_hits[i])

        # Check duplicates
        if (curRatio >= ratio) and (reco_track_id not in reco_tracks):
            trackCandParamsList[i].selected = selected
            trackCandParamsList[i].isDup = False
            trackCandParamsList[i].trackId = reco_track_id
            trackCandParamsList[i].isFake = False

        if (curRatio >= ratio) and (reco_track_id in reco_tracks):
            duplicate_tracks.append(reco_track_id)

            trackCandParamsList[i].selected = selected
            trackCandParamsList[i].isDup = True
            trackCandParamsList[i].trackId = reco_track_id
            trackCandParamsList[i].isFake = False

            continue

        # Check ratio and mark track as reco or fake
        if curRatio >= ratio:
            reco_tracks.add(reco_track_id)

            trackCandParamsList[i].selected = selected
            trackCandParamsList[i].isDup = False
            trackCandParamsList[i].trackId = reco_track_id
            trackCandParamsList[i].isFake = False
        else:
            trackCandParamsList[i].selected = None
            trackCandParamsList[i].isDup = None
            trackCandParamsList[i].trackId = None
            trackCandParamsList[i].isFake = True

            fake_tracks.add(i)

    return reco_tracks, fake_tracks, duplicate_tracks, trackCandParamsList
