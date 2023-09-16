import os
import json

from typing import Any, Dict, Optional


def get_from_env(env_key: str, default: Optional[str] = None) -> str:
    """Get a value from an environment variable."""
    if env_key in os.environ and os.environ[env_key]:
        return os.environ[env_key]
    elif default is not None:
        return default
    else:
        raise ValueError(
            f"Did not find `{env_key}`, please add an environment variable"
        )


def get_from_env_as_json(env_key: str, default: Optional[str] = None) -> list | dict:
    str_ = get_from_env(env_key, default)
    return json.loads(str_)
