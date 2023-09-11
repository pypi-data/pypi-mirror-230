import os

# get relative path by config path (./cvnets/configs)
def config_path(path=""):
    file_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(file_path, "configs", path)