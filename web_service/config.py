"""
Define app setting configurations for development and production.
"""

class Config:
    """
    General settings that apply to all configurations go here.
    """
    APPLICATION_ROOT = '/jupyterhub-container-deploy'
    MAX_DEPLOY = 30

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
