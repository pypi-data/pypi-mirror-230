"""
Module implementing authentication configuration.
"""
from pydantic import BaseSettings


class AuthenticationConfiguration(BaseSettings):
    """
    Simple authentication configuration class
    """
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    hashed_admin_password: str
    admin_user: str
    test_password: str = ''

    class Config:
        """
        Config class specifying the name of the environment file to read
        """
        env_file = '.env'


AUTH = AuthenticationConfiguration()
