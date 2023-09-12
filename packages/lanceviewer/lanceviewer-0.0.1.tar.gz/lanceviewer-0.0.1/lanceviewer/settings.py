import json
import streamlit as st
import base64

from pathlib import Path

# This file is mostly a hack to get support different types schemas in order to make this tool more generic.
# Ideally, we should not need to do this and just check for the data types but there are 2 problems with this:
# 1. Right now all file types are stored as bytes 
# 2. Some schemas are nested, like the current MJ laion_sac

"""
Temp. method to deal with multimodal data in form of bytes. This mapping is used when bytes type is encountered 
in the dataset schema. The key is the column name and the value is the type of the data.
"""
# Key: (Lamdba, Optional[st.column_config])
DEFAULT_TRANSFORMS = {
    'img': (lambda x: "data:image/png;base64," + base64.b64encode(x).decode() if isinstance(x, bytes) else "data:image/png;base64,",
            st.column_config.ImageColumn())
}

MJ_TRANSFORMS = {
    'img': (lambda x: "data:image/png;base64," + base64.b64encode(x[1]).decode() if isinstance(x[1], bytes) else "data:image/png;base64,",
            st.column_config.ImageColumn())
}


TRANSFORMS = {
    "default": DEFAULT_TRANSFORMS,
    "MJ": MJ_TRANSFORMS,
}


CONFIG_PATH = "~/.lanceviewer/config.json"
DEFAULT_CONFIG = {
    "download_remote_data": False,
    "transforms": "MJ",
}


def write_config(config):
    config_path = Path(CONFIG_PATH).expanduser()
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True)
    with open(config_path, "w") as f:
        json.dump(config, f)

def get_config():
    config_path = Path(CONFIG_PATH).expanduser()
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = DEFAULT_CONFIG
        write_config(config)
    
    return config

def should_download_remote_data():
    return get_config().get("download_remote_data", False)

def get_transforms_name():
    return get_config().get("transforms", "default")

def get_transforms():
    return TRANSFORMS[get_transforms_name()]
    