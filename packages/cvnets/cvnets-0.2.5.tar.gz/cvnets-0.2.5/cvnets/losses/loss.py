import torch

def loss(name):
    if name=="CrossEntropyLoss":
        loss_fn = torch.nn.CrossEntropyLoss()
    else:
        raise ValueError(f"'{name}' is invalid name")
    return loss_fn
