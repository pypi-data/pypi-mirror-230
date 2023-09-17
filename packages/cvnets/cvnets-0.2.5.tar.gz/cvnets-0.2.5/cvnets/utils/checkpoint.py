import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
from ..models import create_model


def save_model(model, name="model.pth"):
    os.makedirs(os.path.dirname(name), exist_ok=True)
    torch.save(model.state_dict(), name)
    print(f"Saved PyTorch Model State to {name}")


def load_model(backbone, path, n_dim=None, pretrained=False):
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = "cpu"

    if backbone.startswith("cvnets_"):
        backbone = backbone.replace("cvnets_", "")

    if backbone.startswith("dino"):
        body = torch.hub.load("facebookresearch/dino:main", backbone)
    else:
        body = timm.create_model(backbone, pretrained=False)

    last = NormLayer()
    bdim = 2048 if backbone == "resnet50" else 384
    head = nn.Sequential(nn.Linear(bdim, n_dim), last)
    nn.init.constant_(head[0].bias.data, 0)
    nn.init.orthogonal_(head[0].weight.data)
    rm_head(body)
    model = HeadSwitch(body, head)
    model.load_state_dict(torch.load(path, map_location=device))
    return model


class NormLayer(nn.Module):
    def forward(self, x):
        return F.normalize(x, p=2, dim=1)


def rm_head(m):
    names = set(x[0] for x in m.named_children())
    target = {"head", "fc", "head_dist"}
    for x in names & target:
        m.add_module(x, nn.Identity())


class HeadSwitch(nn.Module):
    def __init__(self, body, head):
        super(HeadSwitch, self).__init__()
        self.body = body
        self.head = head
        self.norm = NormLayer()

    def forward(self, x, skip_head=False):
        x = self.body(x)
        if type(x) == tuple:
            x = x[0]
        if not skip_head:
            x = self.head(x)
        else:
            x = self.norm(x)
        return x
