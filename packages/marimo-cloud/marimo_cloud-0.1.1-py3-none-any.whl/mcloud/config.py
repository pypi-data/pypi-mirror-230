import toml
import os
from pydantic import BaseModel

from typing import Optional

_CREDENTIALS_FILE = "~/.marimo/credentials.toml"

class Credentials(BaseModel):
    created_at: Optional[int]
    expires_at: Optional[int]
    access_token: Optional[str]
    email: Optional[str]

class AppConfiguration(BaseModel):
    app_id: Optional[str]
    app_slug: Optional[str]

def read_credentials() -> Credentials:
    """
    Read credentials from the credentials file.
    """
    path = os.path.expanduser(_CREDENTIALS_FILE)
    try:
        with open(path, "r") as file:
            data = toml.load(file)
            return Credentials(**data)
    except FileNotFoundError:
        return Credentials()

def write_credentials(credentials: Credentials) -> None:
    """
    Write credentials to the credentials file.
    """
    path = os.path.expanduser(_CREDENTIALS_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        toml.dump(credentials.dict(), file)

def delete_credentials() -> None:
    """
    Delete the credentials file.
    """
    path = os.path.expanduser(_CREDENTIALS_FILE)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def read_app_config() -> AppConfiguration:
    """
    Read the app configuration from the mcloud.toml file.
    """
    path = os.path.join(os.getcwd(), "mcloud.toml")
    try:
        with open(path, "r") as file:
            data = toml.load(file)
            return AppConfiguration(**data)
    except FileNotFoundError:
        return AppConfiguration()

def write_app_config(config: AppConfiguration) -> None:
    """
    Write the app configuration to the mcloud.toml file.
    """
    path = os.path.join(os.getcwd(), "mcloud.toml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        toml.dump(config.dict(), file)
