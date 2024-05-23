import torch

from data_processing.cluster_data import create_clusters
from post_processing.cleaning.pytorch_neural_net.NN import FCNeuralNet
from pandas import DataFrame

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train_model(model, train_loader, criterion, optimizer, num_epochs):
    model.train()

    for epoch in range(num_epochs):
        running_loss = 0.0

        for i, info in enumerate(train_loader):
            inputs, labels = info
            optimizer.zero_grad()

            outputs = model(inputs)

            loss = criterion(outputs, labels)

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}")
        torch.save(model.state_dict(), "weight.pth")


def cluster_and_neural_net(track_list: list, track_params: DataFrame, model: FCNeuralNet, shared_hits=3):
    cluster_list = create_clusters(track_list, min_n_shared_hits=shared_hits)
    result_track_list = []
    with torch.no_grad():
        for cluster in cluster_list:
            best_track = []
            best_track_good_prob = -100
            for track in cluster:
                track_id, track_info = list(track.items())[0]

                track_info_tensor = torch.tensor(track_params.iloc[track_id].to_numpy(),
                                                 dtype=torch.float32,
                                                 device=device)
                good_prob = float(model(track_info_tensor))

                if good_prob > best_track_good_prob:
                    best_track = track_info
                    best_track_good_prob = good_prob

            result_track_list.append(best_track)
    return result_track_list
