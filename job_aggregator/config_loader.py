import yaml
import os


def load_sources_config():
        
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_PATH = os.path.join(BASE_DIR, "config", "sources.yaml")

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    return config.get("sources", [])