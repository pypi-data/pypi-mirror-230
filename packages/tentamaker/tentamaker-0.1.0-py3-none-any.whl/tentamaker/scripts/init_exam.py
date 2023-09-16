# Copyright (C) 2023 Anders Logg
# Licensed under the MIT License

import os, shutil


from tentamaker import _version, _dirs, _config_path_system, _config_path_local


def main():
    print(f"This is TentaMaker, version {_version}\n")
    print("Initializing exam...")

    # Create directories (if they don't exist)
    for directory in _dirs:
        if not os.path.exists(directory):
            print("Creating directory '%s'" % directory)
            os.mkdir(directory)
        else:
            print("Directory '%s' already exists" % directory)

    # Add config files
    for file in os.listdir(_config_path_system):
        if not os.path.exists(_config_path_local / file):
            print("Copying config file '%s'" % file)
            shutil.copy(_config_path_system / file, _config_path_local / file)
        else:
            print("Config file '%s' already exists, not overwriting" % file)
