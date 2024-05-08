from statistics import mean
import os

def read_data(data_path, type):
    track_dicts = {}
    with open(data_path) as f:
        for i in f:
            if 'format' in i:
                i = i.replace('# format: ', '')
                i = i.replace('event_number\n', 'event_number')
                info = list(map(str, i.split(", ")))
                track_dict = dict((col, []) for col in info)
                ev_num = 0
            else:
                i = i.replace('True', '1')
                i = i.replace('False', '0')
                i = i.replace('None', '0')
                info = list(map(float, i.split(",")))
                if type == 'cands' and info[2] != 1 and (info[4] <= 0.1 or abs(info[5]) > 1.5):
                    continue
                if type == 'real' and (info[3] <= 0.1 or abs(info[4]) > 1.5):
                    continue
                for i, k in enumerate(track_dict):
                    track_dict[k].append(info[i])
                if ev_num != info[-1]:
                    track_dicts[ev_num] = track_dict
                    ev_num = info[-1]
                    for k in track_dict:
                        track_dict[k] = []
    # track_df = pd.DataFrame.from_dict(track_dict)
    return track_dicts

def calc_fake_rate(is_fake, num_reco):
    num_fake = is_fake.count(1)
    return num_fake/num_reco

def calc_dupl_rate(is_dupl, num_reco):
    num_dupl = is_dupl.count(1)
    return num_dupl/num_reco

def calc_eff(is_reco):
    num_reco = is_reco.count(1)
    return num_reco/len(is_reco)

def calc_chars(track_dict, real_dict, chars):
    if real_dict['is-reco'].count(1) >0:
        num_reco = len(track_dict['event_number'])
        chars['eff'].append(calc_eff(real_dict['is-reco']))
        chars['dupl'].append(calc_dupl_rate(track_dict['isDup'], num_reco))
        chars['fake'].append(calc_dupl_rate(track_dict['isFake'], num_reco))
        return chars
    return chars

def process_events(path_cand, path_real):
    reco_tracks_events = read_data(path_cand, type='cands')
    real_tracks_events = read_data(path_real, type='real')
    all_chars = {'eff': [], 'dupl': [], 'fake': []}
    for event in reco_tracks_events:
        if event in real_tracks_events.keys():
            all_chars = calc_chars(reco_tracks_events[event], real_tracks_events[event], all_chars)
    avg_chars = {}
    avg_chars['avg_eff'] = mean(all_chars['eff'])
    avg_chars['avg_dupl'] = mean(all_chars['dupl'])
    avg_chars['avg_fake'] = mean(all_chars['fake'])
    return avg_chars

def process_methods(dir_path):
    chars = {}
    for filename in os.listdir(dir_path):
        if filename.startswith('track_candidates_'):
            postfix = filename.replace('track_candidates_', '')
            postfix = postfix.replace('.txt', '')
            chars[postfix] = process_events(f'{dir_path}/{filename}', f'{dir_path}/real_tracks_{postfix}.txt')
    return chars


avg_chars = process_methods('chars_data')
for method in avg_chars:
    print(method, '\n', f'Efficiency: {avg_chars[method]["avg_eff"]} \n',
          f'Duplicate rate: {avg_chars[method]["avg_dupl"]}\n',
          f'Fake rate: {avg_chars[method]["avg_fake"]}\n')
