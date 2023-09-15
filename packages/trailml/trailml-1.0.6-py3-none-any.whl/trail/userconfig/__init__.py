import os

from trail.libconfig import libconfig
from trail.userconfig.config import MainConfig
from trail.userconfig.cli_configuration_workflow import get_user_credentials, login_user

primary_config_path = os.path.expanduser(libconfig.PRIMARY_USER_CONFIG_PATH)
secondary_config_path = os.path.expanduser(libconfig.SECONDARY_USER_CONFIG_PATH)

if os.getenv('TRAIL_CONFIG'):
    config_path = os.getenv('TRAIL_CONFIG')
elif os.path.isfile(primary_config_path):
    config_path = primary_config_path
elif os.path.isfile(secondary_config_path):
    config_path = secondary_config_path
else:
    [username, password] = get_user_credentials(
        "Configuration file not found. Please provide required information below."
    )
    login_user(username, password, invalid=False, first=True)
    config_path = secondary_config_path

userconfig = MainConfig(config_path)
