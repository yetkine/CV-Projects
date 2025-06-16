import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np

# CIFAR10 veri setini yükleme
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_dataset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)

# Kombinasyon parametreleri
activation_functions = {"ReLU": torch.relu, "Sigmoid": torch.sigmoid}
batch_sizes = [8, 64]
loss_functions = {"CrossEntropy": nn.CrossEntropyLoss(), "MSE": nn.MSELoss()}
optimizers = {"SGD": lambda params: optim.SGD(params, lr=0.01), "Adam": lambda params: optim.Adam(params, lr=0.001)}

# MLP Modeli tanımı
class MLP(nn.Module):
    def __init__(self, activation):
        super(MLP, self).__init__()
        self.activation = activation
        self.fc1 = nn.Linear(32 * 32 * 3, 512)  # Giriş boyutu CIFAR10 için 32x32x3
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = x.view(-1, 32 * 32 * 3)  # Girdi boyutunu düzleştir
        x = self.activation(self.fc1(x))
        self.features = x  # PCA için özellikleri sakla
        x = self.activation(self.fc2(x))
        x = self.activation(self.fc3(x))
        x = self.fc4(x)
        return x

# Eğitim döngüsü
def train_model(model, train_loader, criterion, optimizer, epochs=5):
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()

            # Model çıktısı
            outputs = model(inputs)

            # MSE Loss için hedefleri one-hot encode et
            if isinstance(criterion, nn.MSELoss):
                labels_one_hot = torch.nn.functional.one_hot(labels, num_classes=10).float()
                loss = criterion(outputs, labels_one_hot)
            else:
                loss = criterion(outputs, labels)

            # Geri yayılım ve optimizasyon
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        print(f"Epoch {epoch+1}, Loss: {running_loss / len(train_loader)}")

# Test döngüsü
def test_model(model, test_loader, criterion):
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    acc = accuracy_score(all_labels, all_preds)
    return all_labels, all_preds, acc

# PCA ve Confusion Matrix çıktıları
def visualize_results(model, test_loader, labels, preds):
    # Karışıklık matrisi
    cm = confusion_matrix(labels, preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.show()

    # PCA görselleştirmesi
    pca = PCA(n_components=2)
    features = []

    # Özellikleri al
    model.eval()
    with torch.no_grad():
        for inputs, _ in test_loader:
            model(inputs)  # features dolduruluyor
            features.append(model.features.cpu().numpy())

    features_2d = pca.fit_transform(np.vstack(features))

    plt.figure(figsize=(8, 6))
    plt.scatter(features_2d[:, 0], features_2d[:, 1], c=labels[:len(features_2d)], cmap='tab10')
    plt.colorbar()
    plt.title("PCA 2D Visualization")
    plt.show()

# Kombinasyonlar için model eğitimi ve değerlendirme
for activation_name, activation_fn in activation_functions.items():
    for batch_size in batch_sizes:
        for loss_name, loss_fn in loss_functions.items():
            for optimizer_name, optimizer_fn in optimizers.items():
                print(f"\nActivation: {activation_name}, Batch Size: {batch_size}, Loss: {loss_name}, Optimizer: {optimizer_name}")

                # Veri yükleyiciler
                train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
                test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

                # Model ve optimizer tanımı
                model = MLP(activation=activation_fn)
                optimizer = optimizer_fn(model.parameters())

                # Eğitim
                train_model(model, train_loader, loss_fn, optimizer)

                # Test
                labels, preds, acc = test_model(model, test_loader, loss_fn)
                print(f"Accuracy: {acc * 100:.2f}%")

                # Görselleştirme
                visualize_results(model, test_loader, labels, preds)
