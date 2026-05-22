import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "YDownload")

DEFAULT_CONFIG = {
    "output_path": DEFAULT_DOWNLOAD_DIR,
    "format_choice": "Best Video (MP4)",
    "quality_choice": "Best Available",
    "browser_cookie": "None",
    "speed_limit": "Unlimited",
    "max_filesize": "Unlimited",
    "playlist_start": "1",
    "playlist_end": "",
    "custom_template": "%(title)s.%(ext)s",
    
    "embed_thumbnail": True,
    "download_subs": False,
    "burn_subs": False,
    "sponsorblock": False,
    "play_sound": True,
    "write_description": False,
    "embed_metadata": True,
    "force_ipv4": False,
    "keep_video": False,
    "auto_shutdown": False,
    "normalize_audio": False,
    "auto_retry": True
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
        
    try:
        with open(CONFIG_FILE, 'r') as f:
            loaded = json.load(f)
            for key in DEFAULT_CONFIG:
                if key not in loaded:
                    loaded[key] = DEFAULT_CONFIG[key]
            return loaded
    except Exception as e:
        print(f"Failed to load config: {e}")
        return DEFAULT_CONFIG

def save_config(config_dict):
    try:
        if not os.path.exists(config_dict["output_path"]):
            os.makedirs(config_dict["output_path"], exist_ok=True)
            
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_dict, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")