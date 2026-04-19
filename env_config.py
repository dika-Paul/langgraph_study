from typing import Any

import yaml
from pathlib import Path


ENV_CONFIG_FILE = Path(__file__).resolve().parent / 'env_config.yaml'

def load_env_config(path: Path = ENV_CONFIG_FILE) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}