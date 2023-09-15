import os

from .config import DevelopmentConfig, ProductionConfig


def is_development_environment():
    return os.getenv('TRAIL_ENV') in ['dev', 'development']


if is_development_environment():
    libconfig = DevelopmentConfig
else:
    libconfig = ProductionConfig
