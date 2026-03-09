import yaml


def load_sources_config():

    with open("config/sources.yaml", "r") as f:
        config = yaml.safe_load(f)

    return config.get("sources", [])