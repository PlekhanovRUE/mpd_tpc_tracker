import torch
from torch.utils.data import Dataset
from torch import optim, nn
from post_processing.cleaning.pytorch_neural_net.NN_dataloader import NNDatasetLoader
from post_processing.cleaning.pytorch_neural_net.NN import FCNeuralNet
from post_processing.cleaning.pytorch_neural_net.NN_utils import train_model
from time import time

# Data preparation
train_dataset = NNDatasetLoader("../../../data/new_format_tracks_data/result.csv", True)
test_dataset = NNDatasetLoader("../../../data/new_format_tracks_data/result.csv", False)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=512, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=512, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = FCNeuralNet().to(device)
criterion = nn.BCELoss(weight=torch.FloatTensor([0.9]).to(device)).to(device)
optimizer = optim.Adam(model.parameters())
num_epochs = 10

if __name__ == "__main__":
    s = time()
    train_model(model, train_loader, criterion, optimizer, num_epochs)
    print(time() - s)

# model = CNN_delay()
# model.load_state_dict(torch.load('weight/CNN_seed_10.pth', map_location=device))
# a = top_k_accuracy(model, test_loader)
