# -*- coding: utf-8 -*-
"""CAP4453_Project2Part2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qnrNKKcOLqJw9D-vN8e3_OmCqJcoU4BM
"""

from __future__ import print_function
import argparse
import os
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torch.utils.tensorboard import SummaryWriter
import numpy as np

class ConvNet(nn.Module):
    def __init__(self, mode):
        super(ConvNet, self).__init__()
        
        # Define various layers here, such as in the tutorial example
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=10, kernel_size=3)
        self.conv2 = nn.Conv2d(in_channels=10, out_channels=10, kernel_size=3)
        self.conv3 = nn.Conv2d(in_channels=3, out_channels=20, kernel_size=3)
        self.conv4 = nn.Conv2d(in_channels=20, out_channels=40, kernel_size=3)
        self.conv5 = nn.Conv2d(in_channels=40, out_channels=40, kernel_size=3)

        self.fc1_model1 = nn.Linear(360, 100)  # This is first fully connected layer for step 1.
        self.fc1_model2 = nn.Linear(1440, 100) # This is first fully connected layer for step 2.
        self.fc1_model3 = nn.Linear(640, 100)  # This is first fully connected layer for step 3
        
        self.fc2 = nn.Linear(100, 10)       # This is 2nd fully connected layer for all models.
        
        self.fc_model0 = nn.Linear(2250, 100)   # This is for example model.
        
        
        # This will select the forward pass function based on mode for the ConvNet.
        # Based on the question, you have 3 modes available for step 1 to 3.
        # During creation of each ConvNet model, you will assign one of the valid mode.
        # This will fix the forward function (and the network graph) for the entire training/testing
        if mode == 1:
            self.forward = self.model_1
        elif mode == 2:
            self.forward = self.model_2
        elif mode == 3:
            self.forward = self.model_3
        elif mode == 0:
            self.forward = self.model_0
        else: 
            print("Invalid mode ", mode, "selected. Select between 1-3")
            exit(0)
        
    
    # Example model. Modify this for step 1-3
    def model_0(self, X):
        # ======================================================================         
        
        X = F.relu(self.conv1(X))
        #print(X.shape)
        X = F.max_pool2d(X, kernel_size=2)
        #print(X.shape)
        
        X = torch.flatten(X, start_dim=1)
        #print(X.shape)
        
        X = F.relu(self.fc_model0(X))
        X = self.fc2(X)
        
        return X
        
    
    # Simple CNN. step 1
    def model_1(self, X):
        # ======================================================================
         
        # Complete this part as model_0, add one more conv2d layer 
        # with relu activation followed by maxpool layer.
        X = F.relu(self.conv1(X))
        X = F.max_pool2d(X, kernel_size=2)
        X = F.relu(self.conv2(X))
        X = F.max_pool2d(X, kernel_size=2)
        X = torch.flatten(X, start_dim=1)

        X = F.relu(self.fc1_model1(X))
        X = self.fc2(X)
        
        return X
        

    # Increase filters. step 2
    def model_2(self, X):
        # ======================================================================
        
        # Complete this part as model_1. Modify in/out channels for conv2d layers.
        X = F.relu(self.conv3(X))
        X = F.max_pool2d(X, kernel_size=2)
        X = F.relu(self.conv4(X))
        X = F.max_pool2d(X, kernel_size=2)
        X = torch.flatten(X, start_dim=1)

        X = F.relu(self.fc1_model2(X))
        X = self.fc2(X)
        
        return X
        

    # Large CNN. step 3
    def model_3(self, X):
        # ======================================================================
        
        # Complete this part as model_2, add one more conv2d layer 
        # with relu activation. Do not add maxpool after this new conv2d layer.
        X = F.relu(self.conv3(X))
        X = F.max_pool2d(X, kernel_size=2)
        X = F.relu(self.conv4(X))
        X = F.max_pool2d(X, kernel_size=2)
        X = F.relu(self.conv5(X))
        X = torch.flatten(X, start_dim=1)

        X = F.relu(self.fc1_model3(X))
        X = self.fc2(X)
        
        return X


def train(model, device, train_loader, optimizer, criterion, epoch, batch_size):
    '''
    Trains the model for an epoch and optimizes it.
    model: The model to train. Should already be in correct device.
    device: 'cuda' or 'cpu'.
    train_loader: dataloader for training samples.
    optimizer: optimizer to use for model parameter updates.
    criterion: used to compute loss for prediction and target 
    epoch: Current epoch to train for.
    batch_size: Batch size to be used.
    '''
    
    # Set model to train mode before each epoch
    model.train()
    
    # Empty list to store losses 
    losses = []
    correct = 0
    
    # Iterate over entire training samples (1 epoch)
    for batch_idx, batch_sample in enumerate(train_loader):
        data, target = batch_sample
        
        # Push data/label to correct device
        data, target = data.to(device), target.to(device)
        # print(data.shape)
        # print(target.shape)
        # exit()
        
        # Reset optimizer gradients. Avoids grad accumulation (accumulation used in RNN).
        optimizer.zero_grad()
        
        # Do forward pass for current set of data
        output = model(data)
        
        # ======================================================================
        # Compute loss based on criterion
        loss = criterion(output,target)
        
        # Computes gradient based on final loss
        loss.backward()
        
        # Store loss
        losses.append(loss.item())
        
        # Optimize model parameters based on learning rate and gradient 
        optimizer.step()
        
        # Get predicted index by selecting maximum log-probability
        pred = output.argmax(dim=1, keepdim=True)
        
        # ======================================================================
        # Count correct predictions overall 
        correct += pred.eq(target.view_as(pred)).sum().item()
        
    train_loss = float(np.mean(losses))
    train_acc = correct / ((batch_idx+1) * batch_size)
    print('Train set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
        float(np.mean(losses)), correct, (batch_idx+1) * batch_size,
        100. * correct / ((batch_idx+1) * batch_size)))
    return train_loss, train_acc
    


def test(model, device, test_loader):
    '''
    Tests the model.
    model: The model to train. Should already be in correct device.
    device: 'cuda' or 'cpu'.
    test_loader: dataloader for test samples.
    '''
    
    # Set model to eval mode to notify all layers.
    model.eval()
    
    losses = []
    correct = 0
    
    # Set torch.no_grad() to disable gradient computation and backpropagation
    with torch.no_grad():
        for batch_idx, sample in enumerate(test_loader):
            data, target = sample
            data, target = data.to(device), target.to(device)
            

            # Predict for data by doing forward pass
            output = model(data)
            
            # ======================================================================
            # Compute loss based on same criterion as training
            loss = F.cross_entropy(output, target, reduction='mean')
            
            # Append loss to overall test loss
            losses.append(loss.item())
            
            # Get predicted index by selecting maximum log-probability
            pred = output.argmax(dim=1, keepdim=True)
            
            # ======================================================================
            # Count correct predictions overall 
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss = float(np.mean(losses))
    accuracy = 100. * correct / len(test_loader.dataset)

    print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
        test_loss, correct, len(test_loader.dataset), accuracy))
    
    return test_loss, accuracy
    

def run_main(FLAGS):
    # Check if cuda is available
    use_cuda = torch.cuda.is_available()
    
    # Set proper device based on cuda availability 
    device = torch.device("cuda" if use_cuda else "cpu")
    print("Torch device selected: ", device)
    
    # Initialize the model and send to device 
    model = ConvNet(FLAGS.mode).to(device)
    # print(model)
    # exit()

    # Initialize the criterion for loss computation 
    criterion = nn.CrossEntropyLoss(reduction='mean')
    
    # Initialize optimizer type 
    optimizer = optim.SGD(model.parameters(), lr=FLAGS.learning_rate, weight_decay=1e-7)
    
    # Create transformations to apply to each data sample 
    # Can specify variations such as image flip, color flip, random crop, ...
    #transform=transforms.Compose([
    #    transforms.ToTensor(),
    #    transforms.Normalize((0.1307,), (0.3081,))
    #    ])
    
    transform = transforms.Compose(
                    [transforms.ToTensor(),
                     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
     
    # Load datasets for training and testing
    # Inbuilt datasets available in torchvision (check documentation online)
    dataset1 = datasets.CIFAR10('./data/', train=True, download=True,
                       transform=transform)
    dataset2 = datasets.CIFAR10('./data/', train=False,
                       transform=transform)
    train_loader = DataLoader(dataset1, batch_size = FLAGS.batch_size, 
                                shuffle=True, num_workers=4)
    test_loader = DataLoader(dataset2, batch_size = FLAGS.batch_size, 
                                shuffle=False, num_workers=4)
    
    best_accuracy = 0.0
    
    # Run training for n_epochs specified in config 
    for epoch in range(1, FLAGS.num_epochs + 1):
        print("\nEpoch: ", epoch)
        train_loss, train_accuracy = train(model, device, train_loader,
                                            optimizer, criterion, epoch, FLAGS.batch_size)
        test_loss, test_accuracy = test(model, device, test_loader)
        
        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            
    print("accuracy is {:2.2f}".format(best_accuracy))
    
    print("Training and evaluation finished")
    
    
if __name__ == '__main__':
    # Set parameters for Sparse Autoencoder
    parser = argparse.ArgumentParser('CNN Exercise.')
    parser.add_argument('--mode',
                        type=int, default=1,
                        help='Select mode between 1-3.')
    parser.add_argument('--learning_rate',
                        type=float, default=0.1,
                        help='Initial learning rate.')
    parser.add_argument('--num_epochs',
                        type=int,
                        default=10,
                        help='Number of epochs to run trainer.')
    parser.add_argument('--batch_size',
                        type=int, default=100,
                        help='Batch size. Must divide evenly into the dataset sizes.')
    parser.add_argument('--log_dir',
                        type=str,
                        default='logs',
                        help='Directory to put logging.')
                        
    FLAGS = None
    FLAGS, unparsed = parser.parse_known_args()
    
    print("Mode: ", FLAGS.mode)
    print("LR: ", FLAGS.learning_rate)
    print("Batch size: ", FLAGS.batch_size)
    
    run_main(FLAGS)

"""Task 4 Analysis

Learning Rate 0.1 - Accuracy: 62.

Time: 4.30 minutes

By the Simple CNN method, it does work much better than Task 3 Model, but it still could work with higher results if a different method was used.

Task 5 Analysis

Learning Rate 0.1 - Accuracy: 68.65.

Several Percentages better than Task 4 Model. Increasing the filters seem to do the trick.

Task 6 Analysis

Learning Rate: 0.1 Accuracy 69.30

Out of the Part 2 Models, Task 6 seems to do the best, despite being a percentage higher than Task 5. This might have to do with the CNN being larger.

Conclusion:
 For Part 2, Task 6 has the best accuracy but not by a crucial amount in comparison to Part 1

"""