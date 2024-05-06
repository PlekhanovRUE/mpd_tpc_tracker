from post_processing.cleaning.direct_cleaning import sort_hits
from selector import select_track_id

from collections import defaultdict
import re


def get_tracks_data(track_path, hit_path, track_consist_of_hit_id=False) -> list:
    hit_list = get_hits(hit_path)
    tracks = []
    track_id = 0
    amount_parameters_in_hit = 0

    with open(track_path) as f:
        for i in f:
            if 'format' in i:
                data_format = re.findall(r'\((.*)\)', i)[0].split(', ')
                amount_parameters_in_hit = len(data_format)
                continue

            if not amount_parameters_in_hit:
                print("Wrong format")
                exit()

            temp = []
            tracks.append([])
            mas = i.split(", ")
            amount_characteristics = 0
            j = 0
            while j < len(mas) or temp:
                if amount_characteristics != amount_parameters_in_hit:
                    temp.append(float(mas[j]))
                    amount_characteristics += 1
                    j += 1
                else:
                    hit_index = int(temp[0])
                    hit_params = hit_list[hit_index][:-1]
                    hit_params.insert(0, hit_index)
                    tracks[track_id].append(hit_index if track_consist_of_hit_id else hit_params)
                    temp = []
                    amount_characteristics = 0
            track_id += 1
    return tracks


def get_trackId_to_hits_dict(path_hits, trackId_to_track_params=None) -> dict:
    hits = defaultdict(list)
    with open(path_hits) as f:
        for i in f:
            if 'format' in i:
                continue

            hit = list(map(float, i.split(", ")))
            hits[int(hit[3])].append(hit[:3])

    track_id_list = list(hits.keys())
    for id_track in track_id_list:
        # Удаляем вторичные треки
        if trackId_to_track_params:
            if not select_track_id(id_track, trackId_to_track_params):
                hits.pop(id_track)
                continue
        hits[id_track] = sort_hits(hits[id_track])
    return hits


def get_hits(path_hits) -> list:
    hits = []
    with open(path_hits) as f:
        for i in f:
            if 'format' in i:
                continue

            hit = list(map(float, i.split(", ")))
            hits.append(hit)
    return hits


def get_trackId_to_track_params(path) -> dict:
    trackId_to_track_params = {}
    with open(path) as f:
        for i in f:
            if 'format' in i:
                continue

            splitted = i.split(",")

            q_str = splitted[6]
            q = float(q_str) # if q_str == 'nan' => q = nan

            info = [
                int(splitted[0]),   # trackId  - key
                int(splitted[1]),   # is primary [0]
                int(splitted[2]),   # nHits      [1]
                float(splitted[3]), # pt         [2]
                float(splitted[4]), # eta        [3]
                q                   # charge     [4]
            ]

            trackId_to_track_params[info[0]] = info[1:]

    return trackId_to_track_params
