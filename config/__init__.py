import os


class ConfigException(Exception):
    pass


def check_config():
    if not (
        POSTGRES_DB
        and POSTGRES_USER
        and POSTGRES_PASSWORD
        and POSTGRES_PORT
        and POSTGRES_HOST
    ):
        raise ConfigException(
            """
            POSTGRES_DB
            POSTGRES_USER
            POSTGRES_PASSWORD
            POSTGRES_PORT
            POSTGRES_HOST
            env vars must be set
            """
        )


POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")

check_config()
