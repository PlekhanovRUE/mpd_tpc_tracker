from statistics import mean
import os
import re
import datetime
import logging


PREFIX_REAL = "real_tracks_"
PREFIX_RECO = "track_candidates_"

prefixes = [PREFIX_REAL, PREFIX_RECO]

PT_MIN = 0.1
PT_MAX = 1.5

INPUT_DIR = "/home/belecky/work/sandbox_github_0/analyse/input_for_fakes_cnt/4_1000"

#DEBUG=False
#VERBOSE=False

def div(divisible, divider):
  res = None
  if divider == 0:
    res = 0
  else:
    res = 1.* divisible / divider
  return res
  

methods = [
        "RAW",
        "HCF",
        "PGM",
        "PGS",
        "PWM",
        "PWS",
        "NNS"
]

class Track_Params(object):
  pt = None
  ev_num = None

  def __setattr__(self, key, value):
    if not hasattr(self, key):
      raise TypeError(f"{self} is a frosen class")
    object.__setattr__(self, key, value)


class Real_track_params(Track_Params):
  reco = None

  def __init__(self, ev_num, pt, reco):
    self.pt = pt
    self.ev_num = ev_num
    self.reco = reco

  EFF = "eff"

  def get_val(self, metrics_type):
    if metrics_type == self.EFF:
      return self.reco
    else:
      raise Exception(
          f"Real_track_params::get_val(): "
          f"metrics_type: actual: {metrics_type}, expected: {self.EFF}")


class Track_cand_params(Track_Params):
  dup = None
  fake = None
  selected = None

  def __init__(self, ev_num, pt, dup, fake, selected):
    self.pt = pt
    self.ev_num = ev_num
    self.dup = dup
    self.fake = fake
    self.selected = selected

  def get_val(self, metrics_type):
    if metrics_type == self.DUP:
      return self.dup
    elif metrics_type == self.FAKE:
      return self.fake
    else:
      raise Exception(
          f"Real_track_params::get_val(): "
          f"metrics_type: actual: {metrics_type}, expected: {self.EFF}")

  DUP = "dup"
  FAKE = "fake"

def read_data(fname, track_type):
  s = datetime.datetime.now()
  logging.debug("read_data() started")
  tr_params_lst = []
  with open(fname) as f:
    tr_params = None
    for line in f:
      if "#" in line:
        continue
      fields = line.split(",")
      ev_num = int(fields[-1])
      if track_type == PREFIX_RECO:

        fake = int(fields[2])
        dup = int(fields[3])
        pt = float(fields[4])
        selected = fields[7]
        if selected == "True":
          selected = 1
        elif selected == "False":
          selected = 0
        else:
          selected = None

        tr_params = Track_cand_params(
            ev_num=ev_num,
            pt=pt,
            fake=fake,
            dup=dup,
            selected=selected)
      elif track_type == PREFIX_REAL:
        pt = float(fields[3])
        reco = int(fields[6])

        tr_params = Real_track_params(
            ev_num=ev_num,
            pt=pt,
            reco=reco)
      else:
        raise Exception(f"Bad track_type: {track_type}; "
                        f"expected: [{PREFIX_RECO}, {PREFIX_REAL}]")

      tr_params_lst.append(tr_params)

  f = datetime.datetime.now()
  logging.debug(f"read_data() finished: {f-s}")
 
  return tr_params_lst
 

def filter_track_candidates(tracks):
  s = datetime.datetime.now()
  logging.debug("filter_track_candidates() started")

  res = []
  for item in tracks[:]:
# don't check for track is primary
# don't check for nHits
    if (item.pt >= 0) and not (PT_MIN < item.pt < PT_MAX):
      continue
    if item.selected == 0:
      continue
    res.append(item)
  return res


def filter_tracks(tracks):
  s = datetime.datetime.now()
  logging.debug("filter_track() started")

  for item in tracks[:]:

# for real tracks:
# don't check for track is primary
# don't check for nHits

    if not (PT_MIN < item.pt < PT_MAX):
      tracks.remove(item)

  f = datetime.datetime.now()
  logging.debug(f"filter_tracks() finished: {f-s}")


def filter_tracks_v2(tracks):
  s = datetime.datetime.now()
  logging.debug("filter_track_v2() started")
  res = []

  for item in tracks:

# for real tracks:
# don't check for track is primary
# don't check for nHits

    if not (PT_MIN < item.pt < PT_MAX):
      continue
    res.append(item)
  f = datetime.datetime.now()
  logging.debug(f"filter_tracks_v2 finished: {f-s}")

  return res


def eval_metrics_total(tracks,
                       track_type, # debug only
                       metrics_type=Real_track_params.EFF):
  logging.debug("eval_metrics_total() started")

  passed = 0
  for track in tracks:
    val = track.get_val(metrics_type)
    if val == 1:
      passed += 1
    elif val == 0:
      pass
    elif val == -1:
      pass
    else:
      raise Exception(
          f"Bad value of metrics {metrics_type}, "
          f"track_type: {track_type}: {val}")
  return passed, len(tracks)
    

def eval_metrics_avg(tracks, track_type, metrics_type=Real_track_params.EFF):
  logging.debug("eval_metrics_avg() started")

  prev_ev = None
  effs = []
  passed = 0 
  total = 0
  for itrack, track in enumerate(tracks):
    curr_ev = track.ev_num
    if prev_ev is None:
      prev_ev = curr_ev

    val = track.get_val(metrics_type)
    if itrack == len(tracks) - 1:
      if val == 0:
        pass
      elif val == 1:
        passed += 1
      elif val == -1:
        pass
      else:
        raise Exception(
            f"Bad value of metrics {metrics_type}, "
            f"track_type: {track_type}: {val}")
      total += 1

    if ((curr_ev != prev_ev) or (itrack == len(tracks) - 1)) and \
        (total != 0):
      eff = 1.*passed / total
      effs.append(eff)
      passed = 0
      total = 0

    if val == 0:
      pass
    elif val == 1:
      passed += 1
    elif val == -1:
      pass
    else:
      raise Exception(
          f"Bad value of metrics {metrics_type}, "
          f"track_type: {track_type}: {val}")

    prev_ev = curr_ev
    total += 1

  res = 0
  if len(effs) > 0:
    res = mean(effs)
  return res, effs


def main(input_dir):
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  logging.basicConfig(level=logging.INFO)
  logging.info(f"input_dir: {input_dir}")

  for method in methods:
    # real tracks
    str_ = f"{method}: "
    fname = os.path.join(input_dir, f"{PREFIX_REAL}{method}.txt")
    logging.debug(fname)
    tracks = read_data(fname, track_type=PREFIX_REAL)
    tracks = filter_tracks_v2(tracks)
 
    #     efficiency total
    nreco, ntotal = eval_metrics_total(tracks, PREFIX_REAL)
    eff_t = div(nreco, ntotal)
    str_ += f"eff_total: {nreco} / {ntotal} = {eff_t:.5}"

    #     efficiency avg
    str_ += ", " 
    eff_avg, _ = eval_metrics_avg(tracks, PREFIX_REAL)
    str_ += f"eff_avg: = {eff_avg:.5}"

    del tracks
    del fname

    # track candidates
    fname = os.path.join(input_dir, f"{PREFIX_RECO}{method}.txt")
    logging.debug(fname)
    tracks = read_data(fname, track_type=PREFIX_RECO)
    for track in tracks:
      logging.debug(
          f"[pt: {track.pt}, ev_n: {track.ev_num}, "
          f"dup: {track.dup}, fake: {track.fake}, sel: {track.selected}] ")
    tracks = filter_track_candidates(tracks)

    logging.debug("\nAfter filter: ")
    for track in tracks:
      logging.debug(
          f"[pt: {track.pt}, ev_n: {track.ev_num}, "
          f"dup: {track.dup}, fake: {track.fake}, sel: {track.selected}] ")
 
    # duplicates total 
    ndup, ntotald = \
        eval_metrics_total(tracks, PREFIX_RECO, Track_cand_params.DUP)
    dup_total = div(ndup, ntotald)
    str_ += ", " 
    str_ += f" dup_rate_total: {ndup} / {ntotald} = {dup_total:.5}"

    # duplicates avg
    dup_avg, dup_avg_lst = eval_metrics_avg(tracks, PREFIX_RECO, Track_cand_params.DUP)
    if logger.isEnabledFor(logging.DEBUG):
      str_ += f", dup_rate_avg: {dup_avg_lst}, {dup_avg:.5}" 
    else:
      str_ += f", dup_rate_avg: {dup_avg:.5}" 

    #     fakes total
    nfakes, ntotalf = eval_metrics_total(
        tracks, PREFIX_RECO, Track_cand_params.FAKE)
    fakes_t = div(nfakes, ntotalf)
    str_ += f", fakes_total: {nfakes} / {ntotalf} = {fakes_t:.7}"

    #     fakes avg
    fakes_avg, fake_avg_lst = eval_metrics_avg(tracks, PREFIX_RECO, Track_cand_params.FAKE)
    if logger.isEnabledFor(logging.DEBUG):
      str_ += f", fakes_avg: {fake_avg_lst}, {fakes_avg:.7}"
    else:
      str_ += f", fakes_avg: {fakes_avg:.7}"

    logging.info(str_)


main(INPUT_DIR)
