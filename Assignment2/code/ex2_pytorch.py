import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
# from torch.utils.tensorboard import SummaryWriter
import sys

# torch.manual_seed(100)
# writer = SummaryWriter('runs/Cifar-10-cnn')

def weights_init(m):
    if type(m) == nn.Linear:
        m.weight.data.normal_(0.0, 1e-3)
        m.bias.data.fill_(0.)

def update_lr(optimizer, lr):
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

#--------------------------------
# Device configuration
#--------------------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device: %s'%device)

#--------------------------------
# Hyper-parameters
#--------------------------------
input_size = 32 * 32 * 3
# hidden_size = [1541]
hidden_size = [1034, 512]
# hidden_size = [1034, 512, 256, 128]
num_classes = 10
num_epochs = 30
batch_size = 256
learning_rate = 1e-3
learning_rate_decay = 0.95
reg=0.001
num_training= 49000
num_validation =1000
train = False

#-------------------------------------------------
# Load the CIFAR-10 dataset
#-------------------------------------------------
norm_transform = transforms.Compose([transforms.ToTensor(),
                                     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
                                     ])
cifar_dataset = torchvision.datasets.CIFAR10(root='datasets/',
                                           train=True,
                                           transform=norm_transform,
                                           download=False)

test_dataset = torchvision.datasets.CIFAR10(root='datasets/',
                                          train=False,
                                          transform=norm_transform,
                                          download=False
                                          )
#-------------------------------------------------
# Prepare the training and validation splits
#-------------------------------------------------
mask = list(range(num_training))
train_dataset = torch.utils.data.Subset(cifar_dataset, mask)
mask = list(range(num_training, num_training + num_validation))
val_dataset = torch.utils.data.Subset(cifar_dataset, mask)

#-------------------------------------------------
# Data loader
#-------------------------------------------------
train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                           batch_size=batch_size,
                                           shuffle=True)

val_loader = torch.utils.data.DataLoader(dataset=val_dataset,
                                           batch_size=batch_size,
                                           shuffle=False)

test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
                                          batch_size=batch_size,
                                          shuffle=False)

#======================================================================================
# Q4: Implementing multi-layer perceptron in PyTorch
#======================================================================================
# So far we have implemented a two-layer network using numpy by explicitly
# writing down the forward computation and deriving and implementing the
# equations for backward computation. This process can be tedious to extend to
# large network architectures
#
# Popular deep-learining libraries like PyTorch and Tensorflow allow us to
# quickly implement complicated neural network architectures. They provide
# pre-defined layers which can be used as building blocks to define our
# network. They also enable automatic-differentiation, which allows us to
# define only the forward pass and let the libraries perform back-propagation
# using automatic differentiation.
#
# In this question we will implement a multi-layer perceptron using the PyTorch
# library.  Please complete the code for the MultiLayerPerceptron, training and
# evaluating the model. Once you can train the two layer model, experiment with
# adding more layers and
#--------------------------------------------------------------------------------------

#-------------------------------------------------
# Fully connected neural network with one hidden layer
#-------------------------------------------------
class MultiLayerPerceptron(nn.Module):
    def __init__(self, input_size, hidden_layers, num_classes):
        super(MultiLayerPerceptron, self).__init__()
        #################################################################################
        # TODO: Initialize the modules required to implement the mlp with given layer   #
        # configuration. input_size --> hidden_layers[0] --> hidden_layers[1] .... -->  #
        # hidden_layers[-1] --> num_classes                                             #
        # Make use of linear and relu layers from the torch.nn module                   #
        #################################################################################
        layers = []
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        self.conv_layer = nn.Sequential(

            # Conv Layer block 1
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Conv Layer block 2
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.05),

            # Conv Layer block 3
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )


        layers.append(nn.Dropout(p=0.2))
        layers.append(nn.Linear(256*4*4, hidden_layers[0]))
        # layers.append(nn.Linear(input_size, hidden_layers[0]))
        layers.append(nn.ReLU(inplace=True))
        for i in range(1, len(hidden_layers)):
            layers.append(nn.Linear(hidden_layers[i-1], hidden_layers[i]))
            layers.append(nn.ReLU(inplace=True))
        layers.append(nn.Dropout(p=0.2))
        layers.append(nn.Linear(hidden_layers[-1], num_classes))

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        #################################################################################
        # TODO: Implement the forward pass computations                                 #
        # Note that you do not need to use the softmax operation at the end.            #
        # Softmax is only required for the loss computation and the criterion used below#
        # nn.CrossEntropyLoss() already integrates the softmax and the log loss together#
        #################################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        x = self.conv_layer(x) #omit this line for base model
        x = x.view(x.size(0), -1)

        out = self.layers(x)
        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        return out

model = MultiLayerPerceptron(input_size, hidden_size, num_classes).to(device)
print(model)
if train:
    model.apply(weights_init)


    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=reg)

    # Train the model
    lr = learning_rate
    total_step = len(train_loader)

    running_loss = 0.0
    for epoch in range(num_epochs):
        for i, (images, labels) in enumerate(train_loader):
            # Move tensors to the configured device
            images = images.to(device)
            labels = labels.to(device)
            #################################################################################
            # TODO: Implement the training code                                             #
            # 1. Pass the images to the model                                               #
            # 2. Compute the loss using the output and the labels.                          #
            # 3. Compute gradients and update the model using the optimizer                 #
            # Use examples in https://pytorch.org/tutorials/beginner/pytorch_with_examples.html
            #################################################################################
            # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
            optimizer.zero_grad()
            predicted = model(images)
            loss = criterion(predicted, labels)
            loss.backward()
            optimizer.step()
            # running_loss += loss.item()
            # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

            if (i+1) % 100 == 0:
                print ('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                       .format(epoch+1, num_epochs, i+1, total_step, loss.item()))
                # writer.add_scalar('training loss',
                #             running_loss / 1000,
                #             epoch * total_step + i)
                # running_loss = 0.0

        # Code to update the lr
        lr *= learning_rate_decay
        update_lr(optimizer, lr)
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                ####################################################
                # TODO: Implement the evaluation code              #
                # 1. Pass the images to the model                  #
                # 2. Get the most confident predicted class        #
                ####################################################
                # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
                output = model(images)
                _, predicted = torch.max(output, dim=1)

                # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            acc = 100 * correct / total
            print('Validataion accuracy is: {} %'.format(acc))
            # writer.add_scalar('Validation Accuracy',
            #                 acc,
            #                 epoch * total_step + i)

    ##################################################################################
    # TODO: Now that you can train a simple two-layer MLP using above code, you can  #
    # easily experiment with adding more layers and different layer configurations   #
    # and let the pytorch library handle computing the gradients                     #
    #                                                                                #
    # Experiment with different number of layers (atleast from 2 to 5 layers) and    #
    # record the final validation accuracies Report your observations on how adding  #
    # more layers to the MLP affects its behavior. Try to improve the model          #
    # configuration using the validation performance as the guidance. You can        #
    # experiment with different activation layers available in torch.nn, adding      #
    # dropout layers, if you are interested. Use the best model on the validation    #
    # set, to evaluate the performance on the test set once and report it            #
    ##################################################################################

    # Save the model checkpoint
    torch.save(model.state_dict(), 'model.ckpt')

else:
    # Run the test code once you have your by setting train flag to false
    # and loading the best model

    best_model = torch.load('model.ckpt') # torch.load()
    model.load_state_dict(best_model)
    # Test the model
    # In test phase, we don't need to compute gradients (for memory efficiency)
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            ####################################################
            # TODO: Implement the evaluation code              #
            # 1. Pass the images to the model                  #
            # 2. Get the most confident predicted class        #
            ####################################################
            # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
            output = model(images)
            _, predicted = torch.max(output, dim=1)


            # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            if total == 1000:
                break

        print('Accuracy of the network on the {} test images: {} %'.format(total, 100 * correct / total))

