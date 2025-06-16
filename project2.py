# comp vision project upload

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, accuracy_score
import torch.nn.functional as F

# Set seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# CIFAR-10 Dataset
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_dataset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)

# Data Loader
def get_dataloaders(batch_size):
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader

# LeNet-5 Model
class LeNet5(nn.Module):
    def __init__(self, activation_function=nn.ReLU):
        super(LeNet5, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
        self.activation = activation_function()
    
    def forward(self, x):
        x = self.pool(self.activation(self.conv1(x)))
        x = self.pool(self.activation(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        x = self.fc3(x)
        return x

# Training Function
def train_model(model, train_loader, criterion, optimizer, loss_name, epochs=5):
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            
            # One-hot encode labels if using MSE
            if loss_name == "MSE":
                labels = F.one_hot(labels, num_classes=10).float()
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {running_loss / len(train_loader)}")

# Fixed Testing Function
def test_model(model, test_loader, loss_name):
    model.eval()
    all_labels = []
    all_preds = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            
            # Handle MSE output
            if loss_name == "MSE":
                outputs = torch.argmax(outputs, dim=1)
            else:
                _, outputs = torch.max(outputs, 1)  # For CrossEntropy, normal predictions
            
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(outputs.cpu().numpy())
    accuracy = accuracy_score(all_labels, all_preds)
    print(f"Accuracy: {accuracy * 100:.2f}%")
    return all_labels, all_preds

# PCA and Confusion Matrix Visualization
def visualize_results(all_labels, all_preds, model, test_loader):
    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

    # PCA Visualization
    features = []
    model.eval()
    with torch.no_grad():
        for inputs, _ in test_loader:
            x = model.pool(model.activation(model.conv1(inputs)))
            x = model.pool(model.activation(model.conv2(x)))
            x = x.view(x.size(0), -1)  # Flatten layer before fully connected layers
            x = model.activation(model.fc1(x))
            features.append(x.cpu().numpy())

    features_2d = PCA(n_components=2).fit_transform(np.vstack(features))

    plt.figure(figsize=(8, 6))
    plt.scatter(features_2d[:, 0], features_2d[:, 1], c=all_labels[:len(features_2d)], cmap="tab10")
    plt.colorbar()
    plt.title("PCA 2D Visualization")
    plt.show()

# Experiment Parameters
batch_sizes = [8, 64]
loss_functions = {'CrossEntropy': nn.CrossEntropyLoss, 'MSE': nn.MSELoss}
optimizers = {'SGD': optim.SGD, 'Adam': optim.Adam}
activations = {'ReLU': nn.ReLU, 'Sigmoid': nn.Sigmoid}

# Run Experiments
results = []

for activation_name, activation_fn in activations.items():
    for batch_size in batch_sizes:
        train_loader, test_loader = get_dataloaders(batch_size)
        for loss_name, loss_fn in loss_functions.items():
            for opt_name, opt_fn in optimizers.items():
                print(f"\nActivation: {activation_name}, Batch Size: {batch_size}, Loss: {loss_name}, Optimizer: {opt_name}")
                model = LeNet5(activation_function=activation_fn)
                
                # Handle one-hot encoding for MSE
                criterion = loss_fn()
                optimizer = opt_fn(model.parameters(), lr=0.001)
                train_model(model, train_loader, criterion, optimizer, loss_name)
                all_labels, all_preds = test_model(model, test_loader, loss_name)
                results.append((activation_name, batch_size, loss_name, opt_name, all_labels, all_preds))
                
                # Visualize Results
                visualize_results(all_labels, all_preds, model, test_loader)

# Summarize Results
print("\nSummary of Results:")
for res in results:
    print(f"Activation: {res[0]}, Batch Size: {res[1]}, Loss: {res[2]}, Optimizer: {res[3]}")
