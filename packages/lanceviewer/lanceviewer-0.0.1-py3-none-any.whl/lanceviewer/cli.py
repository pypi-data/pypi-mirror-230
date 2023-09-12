import argparse
import logging

from lanceviewer.view import launch
from lanceviewer.settings import get_config, write_config, TRANSFORMS

def cli():
    LOGGER = logging.getLogger("logger")
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="LanceViewer")
    parser.add_argument("--download_remote_data", type=str, help="Download remote data", required=False, default=argparse.SUPPRESS)
    parser.add_argument("--transforms", type=str, help="Transforms", required=False, default=argparse.SUPPRESS)
    parser.add_argument("--settings" , action='store_true', help="Display settings")
    args = parser.parse_args()
    config = get_config()
    temp_config = config.copy()
    if args.settings:
        LOGGER.info("Settings:")
        LOGGER.info(config)
        return

    if hasattr(args, "download_remote_data"):
        val = args.download_remote_data.lower()
        if args.download_remote_data not in ["true", "false"]:
            raise ValueError("download_remote_data should be True or False")
        temp_config["download_remote_data"] = val == "true"

    if hasattr(args, "transforms"):
        if args.transforms not in TRANSFORMS:
            raise ValueError(f"transforms should be one of {list(TRANSFORMS.keys())}")
        temp_config["transforms"] = args.transforms

    if config != temp_config:
        write_config(temp_config)
        LOGGER.info("Updated settings")
    
    launch()        
