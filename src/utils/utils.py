import os
from pathlib import Path
import traceback
import shutil

from datetime import datetime
import time
from functools import wraps

def lower_case_keys(obj: dict):
    return {k.lower(): v for k, v in obj.items()}


def as_date_time(time_in_mills):
    return datetime.fromtimestamp(int(time_in_mills/1000)) if time_in_mills is not None else None


def set_to_date_time(vals: dict, key: str):
    time_val = vals.get(key, None)
    vals[key] = as_date_time(time_val)
    vals["str_" + key] = time_val # keep the original
    return vals


def to_date_time(data: [dict], time_key):
    """
    Assumes each row in data has a time_key in epock milliseconds. converts to data-time using Pandas
    """
    return {set_to_date_time(row, time_key) for row in data}


def read_env_variable(env_var: str, default_val) -> str:
    env_val = os.getenv(env_var, None)
    if env_val is None:
        return default_val
    env_val = env_val.strip()
    if env_val == '':
        # this is empty string
        return env_val
    # remove double or single quotes
    if env_val.startswith("'") and env_val.endswith("'"):
        last_idx = env_val.rfind("'")
        actual_val = env_val[1:last_idx]
        actual_val = actual_val.strip()
        return actual_val
    elif env_val.startswith("\"") and env_val.endswith("\""):
        last_idx = env_val.rfind("\"")
        actual_val = env_val[1:last_idx]
        actual_val = actual_val.strip()
        return actual_val
    else:
        return env_val


TRUES = ['1', 'YES', 'Y', "T", "TRUE"]
NOT_TRUES = ["FALSE", 'F', '0', 'NO', 'N']


def to_boolean(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    val = val.upper()
    return val in TRUES
    # anything else is False


def ensure_path(file_path: str, delete=True):
    path = Path(file_path)
    if path.exists() and delete:
        # recursively delete
        shutil.rmtree(file_path, ignore_errors=True)

    path.mkdir(parents=True, exist_ok=True)
