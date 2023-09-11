import PIL
import random
import os
import torchvision.transforms as T
from torchvision import datasets
from torch.utils.data import DataLoader, SubsetRandomSampler


crop = 224
mean_std = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
gray = T.Compose(
        [
            T.Grayscale(3),
            T.RandomResizedCrop(
                crop, scale=(0.2, 1.0), interpolation=PIL.Image.BICUBIC
            ),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(*mean_std),
        ]
    )
train_tr = T.Compose(
        [
            T.RandomResizedCrop(
                crop, scale=(0.2, 1.0), interpolation=PIL.Image.BICUBIC
            ),
            T.RandomHorizontalFlip(),
            T.ToTensor(),
            T.Normalize(*mean_std),
        ]
    )

def data_loader(cfg, phase="train", sampling=None):
    assert phase in ['train', 'val', 'test'], "phase should be include in 'train', 'val', 'test'"
    dataname = cfg['data_name']
    batch_size = cfg['batch_size']
    if dataname == "FashionMNIST":
        # Download training data from open datasets.
        data = datasets.FashionMNIST(
            root="data",
            train=True if phase=="train" else False,
            download=True,
            transform=gray,
        )
    else :
        data = datasets.ImageFolder(
            root=f"{cfg['data_dir']}_{phase}",
            transform=train_tr,
        )
    if sampling is not None:
        print("sampling")
        sampler = SubsetRandomSampler(random.sample(list(range(len(data))), int(len(data)*sampling)))
    else:
        sampler = None
    return DataLoader(data, batch_size=batch_size, sampler=sampler)

def get_data(dataname, batch_size=1, train=False, sampling=None):
    if dataname == "FashionMNIST":
        # Download training data from open datasets.
        data = datasets.FashionMNIST(
            root="data",
            train=train,
            download=True,
            # transform=T.ToTensor(),
            transform=train_tr,
        )
    if sampling is not None:
        print("sampling")
        sampler = SubsetRandomSampler(random.sample(list(range(len(data))), int(len(data)*sampling)))
    else:
        sampler = None
    return DataLoader(data, batch_size=batch_size, sampler=sampler)