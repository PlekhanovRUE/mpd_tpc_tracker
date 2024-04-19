import pandas as pd

import config
import selector
import save_to_files
import math

def replace_hits_to_track_id(tracks, hits):
    tracks_hits = []
    for i in range(len(tracks)):
        tracks_hits.append([])
        for hit in tracks[i]:
            hit_id = int(hit[0])
            truth_track_id = int(hits[hit_id][3])
            tracks_hits[i].append(truth_track_id)
    return tracks_hits


def get_selected_trackIds(trackId_to_track_params):
    selected_trackIds = []

    for trackId in trackId_to_track_params.keys():
      if selector.select(trackId, trackId_to_track_params):
        selected_trackIds.append(trackId)

    return selected_trackIds


class TrackCandParams:
    selected = None
    isDup    = None
    trackId  = None
    isFake   = None
    nHits    = None


def get_characteristics(selected_trackIds, track_candidates, hits, n, ratio):
    reco_tracks = set()
    fake_tracks = set()
    duplicate_tracks = []

    trackCandParamsList = []
    for track in track_candidates:
        params = TrackCandParams()
        trackCandParamsList.append(params)

    # Replace hits in track with id of their real track
    tracks_hits = replace_hits_to_track_id(track_candidates, hits)
    for i in range(len(track_candidates)):

        lenTrackCand = len(track_candidates[i])

        trackCandParamsList[i].nHits = lenTrackCand

        if lenTrackCand < n:
            trackCandParamsList[i].selected = False
            trackCandParamsList[i].isDup    = None
            trackCandParamsList[i].trackId  = None
            trackCandParamsList[i].isFake   = None
            continue

        # Find the most common real track id in reco track
        reco_track_id = max(tracks_hits[i], key=tracks_hits[i].count)

        selected = reco_track_id in selected_trackIds

        curRatio = tracks_hits[i].count(reco_track_id) / len(tracks_hits[i])

        # Check duplicates
        if (curRatio >= ratio) and (reco_track_id not in reco_tracks):
            trackCandParamsList[i].selected = selected
            trackCandParamsList[i].isDup    = False
            trackCandParamsList[i].trackId  = reco_track_id
            trackCandParamsList[i].isFake   = False

        if (curRatio >= ratio) and (reco_track_id in reco_tracks):
            duplicate_tracks.append(reco_track_id)

            trackCandParamsList[i].selected = selected
            trackCandParamsList[i].isDup    = True
            trackCandParamsList[i].trackId  = reco_track_id
            trackCandParamsList[i].isFake   = False

            continue

        # Check ratio and mark track as reco or fake
        if curRatio >= ratio:
            reco_tracks.add(reco_track_id)

            trackCandParamsList[i].selected = selected
            trackCandParamsList[i].isDup    = False
            trackCandParamsList[i].trackId  = reco_track_id
            trackCandParamsList[i].isFake   = False
        else:
            trackCandParamsList[i].selected = None
            trackCandParamsList[i].isDup    = None
            trackCandParamsList[i].trackId  = None
            trackCandParamsList[i].isFake   = True

            fake_tracks.add(i)

    return reco_tracks, fake_tracks, duplicate_tracks, trackCandParamsList


# Calculate multiplicity
def calc_mult(trackId_to_track_params,
              only_pri=False,
              with_hits=False,
              charged=True,
              debug=False):
    mult = 0
    for track_id, params in trackId_to_track_params.items():
        pri   = params[0]
        nHits = params[1]
        q     = params[4]

#       if charged and ((q is None) or (q==0) or math.isnan(q)):
        if charged and ((q==0) or math.isnan(q)):
            continue
        if only_pri and (pri != 1):
            continue
        if with_hits and (nHits == 0):
            continue
        if (debug):
            print(f"calc_mult(): track_id: {track_id}")
        mult += 1
    return mult


def calc_characteristics(track_candidates,
                         hit_list,
                         trackId_to_hits_dict,
                         trackId_to_track_params=None,
                         min_length_real=9,
                         min_length_proto=6,
                         ratio=0.5,
                         method='',
                         mult=0):

    selected_trackIds = get_selected_trackIds(trackId_to_track_params)

    # Get all lists of necessary data
    reco_track_list, fake_track_list, duplicate_track_list, trackCandParamsList = \
            get_characteristics(selected_trackIds,
                                track_candidates,
                                hit_list,
                                min_length_proto,
                                ratio)

    for i, val in enumerate(fake_track_list):
        print(f"Fakes: #{i}; val: {val}, method: {method}")

    print("calc_characteristics(): len(trackCandParamsList): {}".format(
            len(trackCandParamsList)))

    for i, par in enumerate(trackCandParamsList):
      sel     = par.selected
      isDup   = par.isDup
      trackId = par.trackId
      isFake  = par.isFake
      nHits   = par.nHits

      pri = None
      nHitsReal = None
      pt  = None
      eta = None

      if trackId is not None:
        pri       = trackId_to_track_params[trackId][0]
        nHitsReal = trackId_to_track_params[trackId][1]
        pt        = trackId_to_track_params[trackId][2]
        eta       = trackId_to_track_params[trackId][3]

    # Remove short real track from recognized data
    reco_track_list = list(filter(lambda x: x in selected_trackIds, reco_track_list))
    fake_track_list = list(filter(lambda x: x in selected_trackIds, fake_track_list))
    duplicate_track_list = list(filter(lambda x: x in selected_trackIds, duplicate_track_list))

    for ind, val in enumerate(selected_trackIds):
      print(f"selected_trackIds #{ind}: {val}")


    print("Fakes: after selection:n fakes: {} method: {}".format(
            len(fake_track_list), method))

    save_to_files.write_real_tracks(
        selected_trackIds=selected_trackIds,
        real_tracks_is_reco=reco_track_list,
        trackId_to_track_params=trackId_to_track_params,
        mult=mult,
        fname=config.fname_real_tracks.format(method))

    save_to_files.save_track_candidates(
        selected_trackIds=selected_trackIds,
        trackCandParamsList=trackCandParamsList,
        trackId_to_track_params=trackId_to_track_params,
        mult=mult,
        fname=config.fname_track_candidates.format(method))

    # Save table of reco and not reco track_candidates
    # save_recognised_logo(reco_track_list, real_track_list)

    # Calc characteristics
    num_real_track = len(selected_trackIds)
    num_reco_track = len(reco_track_list)
    num_fake_track = len(fake_track_list)
    num_duplicate_track = len(duplicate_track_list)
    num_reco_dupl_track = num_reco_track + num_duplicate_track
    num_proto_track = num_reco_dupl_track + num_fake_track

    characteristic_dict = {
        "efficiency": num_reco_track / num_real_track if num_real_track else 0,
        "fake_rate": num_fake_track / num_proto_track if num_proto_track else 0,
        "duplication_rate": num_duplicate_track / num_proto_track if num_proto_track else 0,
        "purity": num_reco_dupl_track / num_proto_track if num_proto_track else 0,
        "num_recognize_track": num_reco_track,
        "num_real_track": num_real_track,
        "num_duplicate_track": num_duplicate_track,
        "num_proto_track": num_proto_track,
        "num_fake_track": num_fake_track,
        "num_reco_dupl_track": num_reco_dupl_track
    }
    return characteristic_dict


def save_recognised_logo(reco_track_list, real_track_list):
    result_df = pd.DataFrame(columns=["track_id", "is_reco"])
    for i, track_id in enumerate(real_track_list):
        result_df.at[i, "track_id"] = track_id
        result_df.at[i, "is_reco"] = track_id in reco_track_list
    result_df = result_df.sort_values(by=["is_reco"])
    result_df.to_csv("logo.csv", index=False)
