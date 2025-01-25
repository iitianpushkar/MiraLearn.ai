from pathlib import Path
from typing import Any, Dict
import yaml
from ..exceptions import LoadError


def load_yaml(path: Path) -> Dict[str, Any]:
    """Safely load YAML file"""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise LoadError(f"Failed to load YAML from {path}: {str(e)}")


def save_yaml(data: Dict[str, Any], path: Path) -> None:
    """Safely save YAML file"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False
            )
    except Exception as e:
        raise LoadError(f"Failed to save YAML to {path}: {str(e)}")
