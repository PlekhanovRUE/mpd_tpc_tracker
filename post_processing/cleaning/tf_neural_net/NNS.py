import tensorflow.keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from data_processing.cluster_data import create_clusters
import tensorflow as tf
import pandas as pd


class MarginRankingLoss(tf.keras.losses.Loss):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, y_true, y_pred):
        margin = 0.05
        return tf.reduce_mean((tf.maximum(0.0, y_true - y_pred + margin)))


def create_model():
    model = Sequential()
    model.add(Dense(8, input_dim=8, activation='relu', kernel_initializer='random_normal'))
    model.add(Dense(10, activation='relu', kernel_initializer='random_normal'))
    model.add(Dense(15, activation='relu', kernel_initializer='random_normal'))
    model.add(Dense(10, activation='relu', kernel_initializer='random_normal'))
    model.add(Dense(1, activation='sigmoid', kernel_initializer='random_normal'))
    model.compile(loss=MarginRankingLoss(),
                  optimizer=tensorflow.keras.optimizers.legacy.Adam(),
                  metrics=['accuracy'])

    return model


def get_preds_df(event_number, indices, preds):
    df_preds = pd.DataFrame(columns=['track_id', 'pred'])
    df_preds['event'] = event_number
    df_preds['track_id'] = indices
    df_preds['pred'] = preds
    df_preds['new'] = df_preds.apply(lambda x: str(int(x.event)) + '/' + str(int(x.track_id)), axis=1)
    dct_preds = dict(zip(df_preds['new'], df_preds['pred']))
    return dct_preds


def cluster_and_neural_net(model, track_list: list, tracks_for_nn, event_number, indices, hits=3):
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
