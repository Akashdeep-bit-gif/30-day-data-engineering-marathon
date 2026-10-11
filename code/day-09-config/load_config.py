import yaml
import os

def get_config():
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.yaml not found in project root.")
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    cfg = get_config()
    print("✅ Configuration loaded successfully:")
    print(f"  Location: {cfg['location']['name']} ({cfg['location']['latitude']}, {cfg['location']['longitude']})")
    print(f"  Database Target: {cfg['database']['dbname']}")
