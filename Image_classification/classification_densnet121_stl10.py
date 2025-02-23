import os
import zipfile
import torch

import requests
from torch.utils.data import DataLoader
from torchvision import transforms as T
from torchvision.datasets import STL10
from tqdm import tqdm
import torch.nn as nn
from pytorch_quantization import nn as quant_nn
from pytorch_quantization import calib

from examples.models.densenet import densenet121

threads = 8
torch.set_num_threads(threads)

#maybe better performance (Jupyter)
#%env OMP_PLACES=cores
#%env OMP_PROC_BIND=close
#%env OMP_WAIT_POLICY=active

#WSL
os.environ['OMP_PLACES'] = 'cores'
os.environ['OMP_PROC_BIND'] = 'close'
os.environ['OMP_WAIT_POLICY'] = 'active'

import torch
from torchvision import transforms as T
from torchvision.datasets import STL10
from torch.utils.data import DataLoader


def val_dataloader(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225)):

    transform = T.Compose(
        [
            T.Resize(224),  # Resize to 224x224 before applying normalization
            T.ToTensor(),
            T.Normalize(mean, std),
        ]
    )
    dataset = STL10(root="datasets/stl10_data", split='test', download=True, transform=transform)
    dataloader = DataLoader(
        dataset,
        batch_size=64,
        num_workers=0,
        drop_last=True,
        pin_memory=False,
    )
    return dataloader


transform = T.Compose(
    [
        T.Resize(224),  # Resize to 224x224
        T.RandomCrop(224),  # Apply random crop to 224x224
        T.RandomHorizontalFlip(),
        T.ToTensor(),
        T.Normalize(mean = (0.485, 0.456, 0.406), std = (0.229, 0.224, 0.225)),
    ]
)


dataset = STL10(root="datasets/stl10_data", split='train', download=True, transform=transform)


evens = list(range(0, len(dataset), 10))
trainset_1 = torch.utils.data.Subset(dataset, evens)


data = val_dataloader()


data_t = DataLoader(trainset_1, batch_size=128, shuffle=False, num_workers=0)


data_iter = iter(data)
images, labels = next(data_iter)

print(images.shape) 
print(labels.shape) 

def collect_stats(model, data_loader, num_batches):
     """Feed data to the network and collect statistic"""

     # Enable calibrators
     for name, module in model.named_modules():
         if isinstance(module, quant_nn.TensorQuantizer):
             if module._calibrator is not None:
                 module.disable_quant()
                 module.enable_calib()
             else:
                 module.disable()

     for i, (image, _) in tqdm(enumerate(data_loader), total=num_batches):
         model(image.cpu())
         if i >= num_batches:
             break

     # Disable calibrators
     for name, module in model.named_modules():
         if isinstance(module, quant_nn.TensorQuantizer):
             if module._calibrator is not None:
                 module.enable_quant()
                 module.disable_calib()
             else:
                 module.enable()

def compute_amax(model, **kwargs):
 # Load calib result
 for name, module in model.named_modules():
     if isinstance(module, quant_nn.TensorQuantizer):
         if module._calibrator is not None:
             if isinstance(module._calibrator, calib.MaxCalibrator):
                 module.load_calib_amax()
             else:
                 module.load_calib_amax(**kwargs)
         print(F"{name:40}: {module}")
 model.cpu()

# axx_mult = 'exact'
# model = densenet121(pretrained=True, axx_mult = axx_mult)
# model.eval() # for evaluation

# import timeit
# correct = 0
# total = 0

# model.eval()
# start_time = timeit.default_timer()
# with torch.no_grad():
#     for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
#         images, labels = images.to("cpu"), labels.to("cpu")
#         outputs = model(images)
#         _, predicted = torch.max(outputs.data, 1)
#         total += labels.size(0)
#         correct += (predicted == labels).sum().item()
# print(timeit.default_timer() - start_time)
# print('Accuracy of the network on the 10000 test images: %.4f %%' % (
#     100 * correct / total))



axx_mult = 'appro1'
model = densenet121(pretrained=True, axx_mult = axx_mult)
model.eval() # for evaluation

with torch.no_grad():
    stats = collect_stats(model, data_t, num_batches=2)
    amax = compute_amax(model, method="percentile", percentile=99.99)
    
# Inference without retraining
import timeit
correct = 0
total = 0

model.eval()
start_time = timeit.default_timer()
with torch.no_grad():
    for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
        images, labels = images.to("cpu"), labels.to("cpu")
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(timeit.default_timer() - start_time)
print('Accuracy of the network on the 10000 test images: %.4f %%' % (
    100 * correct / total))

# Retraining for 15 epochs
from adapt.references.classification.train import evaluate, train_one_epoch, load_data

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.0001)
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.1)

for epoch in range(15):
    print(f"Epoch {epoch + 1}/15")
    train_one_epoch(model, criterion, optimizer, data_t, "cpu", epoch, 1)
    lr_scheduler.step()

# Inference after retraining
correct = 0
total = 0

model.eval()
start_time = timeit.default_timer()
with torch.no_grad():
    for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
        images, labels = images.to("cpu"), labels.to("cpu")
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(timeit.default_timer() - start_time)
print('Accuracy of the network on the 10000 test images: %.4f %%' % (
    100 * correct / total))


axx_mult = 'appro2'
model = densenet121(pretrained=True, axx_mult = axx_mult)
model.eval() # for evaluation

with torch.no_grad():
    stats = collect_stats(model, data_t, num_batches=2)
    amax = compute_amax(model, method="percentile", percentile=99.99)
    
# Inference without retraining
import timeit
correct = 0
total = 0

model.eval()
start_time = timeit.default_timer()
with torch.no_grad():
    for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
        images, labels = images.to("cpu"), labels.to("cpu")
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(timeit.default_timer() - start_time)
print('Accuracy of the network on the 10000 test images: %.4f %%' % (
    100 * correct / total))

# Retraining for 15 epochs
from adapt.references.classification.train import evaluate, train_one_epoch, load_data

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.0001)
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.1)

for epoch in range(15):
    print(f"Epoch {epoch + 1}/15")
    train_one_epoch(model, criterion, optimizer, data_t, "cpu", epoch, 1)
    lr_scheduler.step()

# Inference after retraining
correct = 0
total = 0

model.eval()
start_time = timeit.default_timer()
with torch.no_grad():
    for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
        images, labels = images.to("cpu"), labels.to("cpu")
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(timeit.default_timer() - start_time)
print('Accuracy of the network on the 10000 test images: %.4f %%' % (
    100 * correct / total))

axx_mult = 'appro3'
model = densenet121(pretrained=True, axx_mult = axx_mult)
model.eval() # for evaluation

with torch.no_grad():
    stats = collect_stats(model, data_t, num_batches=2)
    amax = compute_amax(model, method="percentile", percentile=99.99)
    
# Inference without retraining
import timeit
correct = 0
total = 0

model.eval()
start_time = timeit.default_timer()
with torch.no_grad():
    for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
        images, labels = images.to("cpu"), labels.to("cpu")
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(timeit.default_timer() - start_time)
print('Accuracy of the network on the 10000 test images: %.4f %%' % (
    100 * correct / total))

# Retraining for 15 epochs
from adapt.references.classification.train import evaluate, train_one_epoch, load_data

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.0001)
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.1)

for epoch in range(15):
    print(f"Epoch {epoch + 1}/15")
    train_one_epoch(model, criterion, optimizer, data_t, "cpu", epoch, 1)
    lr_scheduler.step()

# Inference after retraining
correct = 0
total = 0

model.eval()
start_time = timeit.default_timer()
with torch.no_grad():
    for iteraction, (images, labels) in tqdm(enumerate(data), total=len(data)):
        images, labels = images.to("cpu"), labels.to("cpu")
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(timeit.default_timer() - start_time)
print('Accuracy of the network on the 10000 test images: %.4f %%' % (
    100 * correct / total))