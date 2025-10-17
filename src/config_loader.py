#!/usr/bin/env python3

import yaml
from pathlib import Path


class ConfigLoader:
    @staticmethod
    def load(config_path="cfg/config.yaml"):
        config_file = Path(config_path)
        if not config_file.exists():
            config_file = Path(__file__).parent.parent / config_path
        
        with open(config_file, "r") as f:
            return yaml.safe_load(f)

