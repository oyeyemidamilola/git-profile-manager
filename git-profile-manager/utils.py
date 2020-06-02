""" Utility functions """
import os
import shutil
import configparser
import sys
import subprocess


SHELL = os.getenv("SHELL", "")
HOME =  os.path.expanduser("~")
# Directory to store all git-profile-manager config
GIT_PROFILE_DIR = os.path.join(HOME, ".gitprofiles")

GLOBAL_GITCONFIG = os.path.join(GIT_PROFILE_DIR, "global")
# Store config for current active user
PROFILE_RC=os.path.join(GIT_PROFILE_DIR, ".profilerc")

GIT_CONFIG = os.path.join(HOME, '.gitconfig')

def get_user_config_path(username):
    """ Get the path to user config """
    return os.path.join(GIT_PROFILE_DIR, username)

def user_exists(username):
    """ A user exists if the corresponding config file is present """
    return os.path.exists(get_user_config_path(username))

def get_unix_profile():
    """ get the profiles for the shell """
    profiles = []
    if "zsh" in SHELL:
        profile = os.path.join(HOME, ".zshrc")

    bash_profile = os.path.join(HOME, ".bashrc")
    if os.path.exists(bash_profile):
        profiles.append(bash_profile)
    return profiles

def user_input(prompt):
    """ User input string for python independent version """

    if sys.version_info >= (3, 0):
        return input(prompt)
    return raw_input(prompt)

def exec_command(command):
    comp = subprocess.run(command)
    if comp.returncode != 0:
        sys.exit(1)
    return comp

def update_current_user(user):
    config = configparser.ConfigParser()
    config.read(PROFILE_RC)
    try:
        config["current"]["user"] = user
    except KeyError:
        config["current"] = {}
        config["current"]["user"] = user

    with open(PROFILE_RC, 'w') as configfile:
        config.write(configfile)


def set_active_user(user):
    current_user = get_current_user()
    update_current_user(user)

    # load config and override global configuration
    config = configparser.ConfigParser()
    config.read(GLOBAL_GITCONFIG)
    config.read(get_user_config_path(user))

    print(config._sections, GIT_CONFIG)

    with open(GIT_CONFIG, "w") as configfile:
        config.write(configfile)


def get_current_user():
    """ Get the current active user """
    config = configparser.ConfigParser()
    config.read(PROFILE_RC)
    current_user = None
    try:
        current_user = config["current"]["user"]
    except KeyError:
        pass
    return current_user
        
def get_all_users():
    users = [f for f in os.listdir(GIT_PROFILE_DIR) if os.path.isfile(os.path.join(GIT_PROFILE_DIR, f)) and f not in [".profilerc", "global"]]
    return users

def save_current_user_profile():
    current_user = get_current_user()

    # Remove entries that match in global config
    global_config = configparser.ConfigParser()
    global_config.read(GLOBAL_GITCONFIG)

    current_config = configparser.ConfigParser()
    current_config.read(GIT_CONFIG)

    # Delete every matching config in both files
    for section in current_config:
        if section in global_config._sections.keys():
            for key, value in current_config[section].items():
                if key in global_config[section].keys():
                    if value == global_config[section][key]:
                        del current_config[section][key]

    # remove sections with no entry
    for section in current_config:
        if section != "DEFAULT" and len(current_config[section].keys()) == 0:
            del current_config[section]

    # Write current user config
    with open(get_user_config_path(current_user), "w") as configfile:
        current_config.write(configfile)

    