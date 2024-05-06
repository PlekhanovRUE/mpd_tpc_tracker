import config


def select_track_id(
    trackId,
    trackId_to_track_params,
    n_real_hits_min=None,  # by default get value from config
    only_charged=None):    # by default get value from config

  if trackId not in trackId_to_track_params:
    raise("select_track_id(): trackId not in trackId_to_track_params")
  params = trackId_to_track_params[trackId]
  pri    = params[0]
  n_hits = params[1]
  pt     = params[2]
  eta    = params[3]
  q      = params[4]
  if config.only_primary and (not pri):
    return False
  if (pt < config.pt_min) or (pt > config.pt_max):
    return False
  if (eta < config.eta_min) or (eta > config.eta_max):
    return False
  hits_min = n_real_hits_min if n_real_hits_min is not None \
                             else config.n_real_hits_min
  if n_hits < hits_min:
    return False
  only_charged = only_charged if only_charged is not None \
                              else config.only_charged
  if only_charged and (q == 0):
    return False

  return True


def select_with_hits(
    trackId,
    trackId_to_track_params):
  return select_track_id(
        trackId,
        trackId_to_track_params,
        n_real_hits_min=1,
        only_charged=False)


def select_charged(
    trackId,
    trackId_to_track_params):
  return select_track_id(
      trackId,
      trackId_to_track_params,
      n_real_hits_min=0,
      only_charged=True)


def select_track_ids(trackId_to_track_params):
  selected_track_ids = []
  for track_id in trackId_to_track_params:
    if select_track_id(track_id, trackId_to_track_params):
      selected_track_ids.append(track_id)
  return selected_track_ids


def select_track_ids_charged(trackId_to_track_params):
  selected_track_ids = []
  for track_id in trackId_to_track_params:
    if select_charged(track_id, trackId_to_track_params):
      selected_track_ids.append(track_id)

  return selected_track_ids


def select_track_ids_with_hits(trackId_to_track_params):
  selected_track_ids = []
  for track_id in trackId_to_track_params:
    if select_with_hits(track_id, trackId_to_track_params):
      selected_track_ids.append(track_id)

  return selected_track_ids
