import json
import os

CACHE_FILE = os.path.join(os.path.dirname(__file__), '../../satellite_cache.json')

SECTIONS = ["basic", "technical", "launch", "cost"]

def normalize_satellite_name(name):
    return ''.join(e for e in name.lower() if e.isalnum())

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except Exception:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_from_cache(name, section):
    cache = load_cache()
    key = normalize_satellite_name(name)
    return cache.get(key, {}).get(section)

def save_to_cache(name, section, data):
    cache = load_cache()
    key = normalize_satellite_name(name)
    if key not in cache:
        cache[key] = {}
    cache[key][section] = data
    save_cache(cache)

def export_cache_as_rows():
    cache = load_cache()
    rows = []
    for sat_name, sat_data in cache.items():
        row = {"satellite_name": sat_name}
        for section in SECTIONS:
            section_data = sat_data.get(section, {})
            for k, v in section_data.items():
                row[f"{section}_{k}"] = v
        rows.append(row)
    return rows 