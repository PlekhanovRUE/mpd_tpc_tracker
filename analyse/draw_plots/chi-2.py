from data_processing.parse_data import get_hits
import pandas as pd
import re

def get_tracks_data(track_path, hit_path) -> list:
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
            mas = i.split(",")
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
                    hit_params.append(float(temp[5]))
                    tracks[track_id].append(hit_params)
                    temp = []
                    amount_characteristics = 0
            track_id += 1
    return tracks


tracks = get_tracks_data("data/event_0_prototracks.txt", "data/event_0_space_points.txt")
track_l = []
chi_l = []
num_points_l = []
chi_len = []
i = 0
for track in tracks:
    chi = sum([hit[-1] for hit in track])
    num_points = len(track)

    chi_len.append(chi / num_points)

    track_l.append(i)
    chi_l.append(chi)
    num_points_l.append(num_points)
    i += 1

df = pd.DataFrame()
df['track'] = track_l
df['chi'] = chi_l
df['len_track'] = num_points_l
df['chi/len'] = chi_len

df.to_csv('chi.csv', index=False)
