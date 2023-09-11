import yaml
from tap import Tap
from ..utils import config_path


def configs(cfg, **kwargs):
    cfg_output = {}
    cfg = config_path(f"base/{cfg}")
    with open(cfg) as f:
        cfg_output.update(yaml.load(f, Loader=yaml.FullLoader))

    with open(config_path(cfg_output["data"])) as f:
        cfg_output.update(yaml.load(f, Loader=yaml.FullLoader))
    del cfg_output['data']

    with open(config_path(cfg_output["model"])) as f:
        cfg_output.update(yaml.load(f, Loader=yaml.FullLoader))
    del cfg_output['model']

    return cfg_output


class Config(Tap):
    path: str = "/Users/jihoon.kim/task/dataset/SOP"  # path to datasets
    num_samples: int = 2  # how many samples per each category in batch
    bs: int = 900  # batch size per GPU, e.g. --num_samples 3 --bs 900 means each iteration we sample 300 categories with 3 samples
    lr: float = 1e-5  # learning rate
    t: float = 0.2  # cross-entropy temperature
    emb: int = 128  # output embedding size
    freeze: int = 0  # number of blocks in transformer to freeze, None - freeze nothing, 0 - freeze only patch_embed
    ep: int = 100  # number of epochs
    hyp_c: float = 0.1  # hyperbolic c, "0" enables sphere mode
    eval_ep: str = "[100]"  # epochs for evaluation, [] or range "r(start,end,step)", e.g. "r(10,70,20)+[200]" means 10, 30, 50, 200"""
    model: str = "dino_vits16"  # model name from timm or torch.hub, i.e. deit_small_distilled_patch16_224, vit_small_patch16_224, dino_vits16
    save_emb: bool = False  # save embeddings of the dataset after training
    emb_name: str = "emb"  # filename for embeddings
    clip_r: float = 2.3  # feature clipping radius
    resize: int = 224  # image resize
    crop: int = 224  # center crop after resize