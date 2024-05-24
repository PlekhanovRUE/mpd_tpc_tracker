# import sys
# sys.path.append('../')
import pandas as pd
import tensorflow.keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from data_processing.parse_data import get_tracks_data
from data_processing.cluster_data import create_clusters
from data_processing.parse_data import *

import tensorflow as tf

class margin_ranking_loss(tf.keras.losses.Loss):
  def __init__(self):
    super().__init__()
  def call(self, y_true, y_pred):
    margin = 0.05
    return tf.reduce_mean((tf.maximum(0.0, y_true - y_pred + margin)))
  

def create_model():
    model = Sequential()
    model.add(Dense(8, input_dim=8, activation='relu',
                    kernel_initializer='random_normal'))
    model.add(Dense(10,activation='relu',kernel_initializer='random_normal'))
    model.add(Dense(15,activation='relu',kernel_initializer='random_normal'))
    model.add(Dense(10,activation='relu',kernel_initializer='random_normal'))
    model.add(Dense(1,activation='sigmoid',
                    kernel_initializer='random_normal'))
    model.compile(loss=margin_ranking_loss(),
                optimizer=tensorflow.keras.optimizers.legacy.Adam(),
                metrics =['accuracy'])
    
    return model

   
def get_preds_df(event_number, indices, preds):
    df_preds = pd.DataFrame(columns=['track_id', 'pred'])
    df_preds['event'] = event_number
    df_preds['track_id'] = indices
    df_preds['pred'] = preds
    df_preds['new'] = df_preds.apply(lambda x: str(int(x.event)) + '/' + str(int(x.track_id)) , axis=1)
    dct_preds = dict(zip(df_preds['new'], df_preds['pred']))
    return dct_preds

# track_list = get_tracks_data('data\event_0_prototracks.txt', 'data\event_0_space_points.txt')
def cluster_and_neural_net(model, track_list: list, tracks_for_nn, event_number, indices, hits=3):
    '''
        dct_preds - выход нейросети
    '''


    track_scores = model.predict(tracks_for_nn)
    dct_preds = get_preds_df(event_number, indices, track_scores)
    clusters = create_clusters(track_list, min_n_shared_hits=hits)
    event_curr_good = []
    for cluster in clusters:
        max_score = 0
        best_track = None
        for dct in cluster:
            track_id = [*dct][0]
            hits = dct[track_id]
            if dct_preds[f'{event_number.unique()[0]}/{track_id}'] > max_score:
                max_score = dct_preds[f'{event_number.unique()[0]}/{track_id}']
                best_track = hits
        event_curr_good.append(best_track)
    return event_curr_good


def leading_track(event_num, hits=3):
    track_list = get_tracks_data(f"../data/event_{event_num}_prototracks.txt", f"../data/event_{event_num}_space_points.txt", True)
    clusters = create_clusters(track_list, min_n_shared_hits=hits)
    event_curr_good = []
    for cluster in clusters:
        for dct in cluster:
            track_id = [*dct][0]
            hits = dct[track_id]
            event_curr_good.append(hits)
            break
    # trackId_to_hits_dict = get_trackId_to_hits_dict(f"../data/event_{event_num}_space_points.txt")
    # hit_list = get_hits(f"../data/event_{event_num}_space_points.txt")
    # trackId_to_track_params = get_trackId_to_track_params(f"../data/event_{event_num}_trackIds.txt")

    # characteristic_dict = validation.calc_characteristics(event_curr_good, hit_list, trackId_to_hits_dict, trackId_to_track_params)
    # return characteristic_dict

    return event_curr_good
    

def neural_net(df_path: str):
    '''
     так как для нейросетки используется большой файл с разными событиями,
     кластеризацией обрабатываются тоже разные события за раз
     возвращается словарь треков, где ключ - номер события
     если надо поправить, скажи
     возможно придется добавлять в сравнение вне цикла
    '''
#   df = pd.read_csv(df_path, sep=", ", engine='python')
    df = pd.read_csv(df_path, sep=",", engine='python')
    df['good'] = df['duplicate'] == df['fake']
    df['good'].astype('int8')
    indexes = df['prototrackIndex']
    event_number = df['#format: eventNumber']
    df.drop(labels=['#format: eventNumber', 'prototrackIndex'], axis=1, inplace=True)
    y = df['good'].astype('float32')
    X = df.iloc[:, :-3]

    model = create_model()
    checkpoint_path = "cp.ckpt"
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1)
    model.fit(X, y, validation_split = 0.25, batch_size =64,
          callbacks=[cp_callback],verbose=2,epochs=5)
    
    preds = model.predict(X)

    df_preds = pd.DataFrame(columns=['track_id', 'pred'])
    df_preds['event'] = event_number
    df_preds['track_id'] = indexes
    df_preds['pred'] = preds
    df_preds['new'] = df_preds.apply(lambda x: str(int(x.event)) + '/' + str(int(x.track_id)) , axis=1)
    dct_preds = dict(zip(df_preds['new'], df_preds['pred']))

    return dct_preds

