#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is to factor out values that might become configurable values later.

Created on Mon May 14 00:57:42 2024

@author: juergen
"""

from pathlib import Path
import yaml


PATH_WORK_DIR = Path.cwd()
PATH_CONFIG_DIR = PATH_WORK_DIR
PATH_CONFIG_FILE = PATH_CONFIG_DIR / "config_local.yaml"
PATH_CONFIG_TEMPLATE = PATH_CONFIG_DIR / "config_template.yaml"

CONFIG = None


def initialize_global_config():
    """
    Read the global config or create a new one

    Returns
    -------
    dict.
    """
    global CONFIG
    global PATH_CONFIG_FILE
    global PATH_CONFIG_TEMPLATE
    if PATH_CONFIG_FILE.exists():
        CONFIG = read_config(PATH_CONFIG_FILE)
    elif PATH_CONFIG_TEMPLATE.exists():
        CONFIG = read_config(PATH_CONFIG_TEMPLATE)
    else:
        # no configuration found - create a new one
        CONFIG = {}
    return CONFIG


def write_global_config():
    """
    Read the global config

    Returns
    -------
    None.
    """
    global CONFIG
    write_config(CONFIG)


def read_config(path : Path=PATH_CONFIG_FILE):
    """
    Read the configuration

    Parameters
    ----------
    path : Path, optional
        Path to the yaml file that contains the config values. 
        The default is path_config_dir.

    Returns
    -------
    dict.
    """
    with path.open("rt") as fp_yaml:
        config = yaml.safe_load(fp_yaml)
    return config


def write_config(config : dict, path : Path=PATH_CONFIG_FILE):
    """
    Read the configuration

    Parameters
    ----------
    config : dict
        Configuration.
        
    path : Path, optional
        Path to the yaml file that contains the config values. 
        The default is path_config_dir.

    Returns
    -------
    dict.
    """
    with path.open("wt") as fp_yaml:
        yaml.dump(config, fp_yaml)


