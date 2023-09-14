import os


class ConfigException(Exception):
    pass


def check_config():
    if not (
        PG_DATABASE
        and POSTGRES_USER
        and POSTGRES_PASSWORD
        and POSTGRES_PORT
        and POSTGRES_HOST
    ):
        raise ConfigException(
            """
            PG_DATABASE
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
PG_DATABASE = os.getenv("PG_DATABASE")

check_config()
