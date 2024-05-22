from torch.utils.data import Dataset
import pandas as pd
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class NNDatasetLoader(Dataset):
    def __init__(self, tracks_params_path: str, is_train: bool):
        tracks_params = pd.read_csv(tracks_params_path)
        if is_train:
            tracks_params = tracks_params[tracks_params["#format:eventNumber"] > 500]
        else:
            tracks_params = tracks_params[tracks_params["#format:eventNumber"] < 500]

        # Create mark info
        good_tracks_info = (tracks_params["duplicate"] == tracks_params["fake"]).astype(int).to_numpy()

        self.data_y = torch.tensor(good_tracks_info,
                                   dtype=torch.float32,
                                   device=device).view(-1, 1)

        self.data_x = torch.tensor(tracks_params.iloc[:, 2:-2].to_numpy(),
                                   dtype=torch.float32,
                                   device=device)

    def __getitem__(self, index):
        return self.data_x[index], self.data_y[index]

    def __len__(self):
        return len(self.data_x)
