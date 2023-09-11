import torch

def optim(name, model, lr=1e-5):
    if name=="SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    elif name=="AdamW":
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    return optimizer
