import os

def write_real_tracks_header(fname):
    with open(fname, 'w') as f:
        f.write('# format: trackId, is-primary, nHits, pt, eta, multiplicity_charged_primary, '
                'is-reco, event_number' + os.linesep)

def write_real_tracks(
        selected_trackIds,
        real_tracks_is_reco,
        trackId_to_track_params,
        mult,
        event_number,
        fname):
    with open(fname, 'a') as f:
        for trackId in selected_trackIds:
            params = trackId_to_track_params[trackId]
            pri    = params[0]
            n_hits = params[1]
            pt     = params[2]
            eta    = params[3]

            is_reco = int(trackId in real_tracks_is_reco)
            f.write(f'{trackId},{pri},{n_hits},{pt},{eta},{mult},'
                    f'{is_reco},{event_number}' + os.linesep)


def write_track_candidates_header(fname):
    with open(fname, 'w') as f:
        f.write("# format: isPrimary, nHits, isFake, isDup, pt, eta, "
                "multiplicity_charged_primary, selected, trackId, event_number" + os.linesep)


def to_int(val):
  if val is None: 
      return -1
  else: 
      return int(val)


def save_track_candidates(
        selected_trackIds,
        trackCandParamsList,
        trackId_to_track_params,
        mult,
        event_number,
        fname):

    print("save_track_candidates(): len(trackCandParamsList): {}".format(
            len(trackCandParamsList)))
    with open(fname, 'a') as f:
        ipnb = -1
        for params in trackCandParamsList:

            selected = params.selected

            isDup   = to_int(params.isDup)
            isFake  = to_int(params.isFake)
            trackId = to_int(params.trackId)

            isPri = -1
            nHits = -1
            pt    = -1
            eta   = -123

            if True:
                ipnb += 1
                print("save_track_candidates(): #{ipnb}; "
                      "selected: {selected}; "
                      "isDup: {isDup}; "
                      "isFake: {isFake}; "
                      "trackId: {trackId}; "
                      "isPri: {isPri}; "
                      "nHits: {nHits}; "
                      "pt: {pt}; "
                      "eta: {eta}".format(
                              ipnb=ipnb,
                              selected=params.selected,
                              isDup=params.isDup,
                              isFake=params.isFake,
                              trackId=params.trackId,
                              isPri=isPri,
                              nHits=nHits,
                              pt=pt,
                              eta=eta)
                      )

            if trackId != -1:
                if trackId not in selected_trackIds:
                    continue

                isPri = trackId_to_track_params[trackId][0]
                nHits = trackId_to_track_params[trackId][1]
                pt    = trackId_to_track_params[trackId][2]
                eta   = trackId_to_track_params[trackId][3]

            f.write(f"{isPri},{nHits},{isFake},{isDup},{pt},{eta},"
                    f"{mult},{selected},{trackId},{event_number}" + os.linesep)


