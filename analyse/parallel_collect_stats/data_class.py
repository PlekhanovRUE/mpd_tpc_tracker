from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional

import torch
from pandas import Series, DataFrame

import os

import save_to_files
from analyse.parallel_collect_stats.utils import load_csv
from post_processing import FCNeuralNet


@dataclass
class MlModelData:
    weigh_file_path: str

    params_file_path: Optional[str] = None
    indices: Series = field(init=False)
    event_num_ser: Series = field(init=False)
    event_df: DataFrame = field(init=False)

    def calc_event_filed(self, event_num: int, input_dir):
        if self.__is_one_params_file__:
            self.event_df = self.base_df[self.base_df['#format:eventNumber'] == event_num]
        else:
            ml_params_fname = f"{input_dir}{os.sep}event_{event_num}_" \
                    "track_candidates_params.txt"
            self.event_df = load_csv(ml_params_fname)

        self.event_df = self.event_df.iloc[:, 2:-2]

    def __post_init__(self):
        self.model = self.__load_model__()
        self.__is_one_params_file__ = bool(self.params_file_path)

        if self.__is_one_params_file__:
            self.base_df: DataFrame = load_csv(self.params_file_path)

    def __load_model__(self):
        model = FCNeuralNet()
        model.load_state_dict(torch.load(self.weigh_file_path, map_location=torch.device("cpu")))
        model.eval()
        return model


@dataclass
class BaseTrackParams:
    selected_trackIds: list
    method: str
    trackId_to_track_params: list
    mult_h: int
    mult_ch: int
    event_number: int


@dataclass
class RealTrackParams(BaseTrackParams):
    reco_track_list: list


@dataclass
class CandTrackParams(BaseTrackParams):
    trackCandParamsList: list


@dataclass
class OneEventRealTrackParams:
    all_method_for_real_tracks: list[RealTrackParams] = field(default_factory=list)
    all_method_for_cand_tracks: list[CandTrackParams] = field(default_factory=list)

    def save_characteristics(self):
        # Save real track characteristics
        for real_track_characteristics in self.all_method_for_real_tracks:
            save_to_files.write_real_tracks(
                selected_trackIds=real_track_characteristics.selected_trackIds,
                real_tracks_is_reco=real_track_characteristics.reco_track_list,
                fname=real_track_characteristics.method,
                trackId_to_track_params=real_track_characteristics.trackId_to_track_params,
                mult_ch=real_track_characteristics.mult_ch,
                mult_h=real_track_characteristics.mult_h,
                event_number=real_track_characteristics.event_number
            )
        # Save cand track characteristics
        for cand_track_characteristics in self.all_method_for_cand_tracks:
            save_to_files.save_track_candidates(
                selected_trackIds=cand_track_characteristics.selected_trackIds,
                trackCandParamsList=cand_track_characteristics.trackCandParamsList,
                trackId_to_track_params=cand_track_characteristics.trackId_to_track_params,
                fname=cand_track_characteristics.method,
                mult_h=cand_track_characteristics.mult_h,
                mult_ch=cand_track_characteristics.mult_ch,
                event_number=cand_track_characteristics.event_number
            )


@dataclass
class HitData:
    tracks: list[float]


@dataclass
class TrackData:
    tracks: list[HitData]


@dataclass
class InputEventData:
    hits_list: list[HitData]
    track_id_to_track_params: dict[int, list[float]]
    _tracks: list[TrackData] = field(default_factory=list, repr=False)

    @property
    def tracks(self) -> list[TrackData]:
        return deepcopy(self._tracks)

    @tracks.setter
    def tracks(self, value: list[TrackData]):
        self._tracks = value
