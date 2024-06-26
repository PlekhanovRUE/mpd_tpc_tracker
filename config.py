from dataclasses import dataclass


@dataclass
class SettingParams:
    # Efficiency calc settings
    pt_min: int = 0
    pt_max: int = 10
    eta_min: float = -2.11
    eta_max: float = 2.11
    n_real_hits_min: int = 9
    only_primary: bool = True
    only_charged: bool = True
    n_proto_hits_min: int = 6
    ratio: float = 0.5

    # Start settings
    start_event: int = 2
    end_event: int = 2
    num_workers: int = 4

    # Result stats files settings
    fname_real_tracks: str = "real_tracks_{}.txt"
    fname_track_candidates: str = "track_candidates_{}.txt"
