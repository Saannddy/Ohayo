import json
import os

PROFILES_PATH = os.path.expanduser("~/.ohayo_profiles.json")


def _read() -> dict:
    if not os.path.exists(PROFILES_PATH):
        return {}
    try:
        with open(PROFILES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _write(data: dict):
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_profiles() -> dict:
    return _read()


def get_profile_names() -> list:
    return list(_read().keys())


def save_profile(name: str, data: dict):
    profiles = _read()
    profiles[name] = data
    _write(profiles)


def load_profile(name: str) -> dict:
    return _read().get(name, {})


def delete_profile(name: str):
    profiles = _read()
    profiles.pop(name, None)
    _write(profiles)
