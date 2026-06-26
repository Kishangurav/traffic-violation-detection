import yaml

class Config:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

    def get(self, *keys):
        val = self.cfg
        for key in keys:
            val = val[key]
        return val