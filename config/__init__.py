import os


class ConfigException(Exception):
    pass


def check_config():
    if not (
        PG_DATABASE
        and PG_USER
        and PG_PASSWORD
        and PG_PORT
        and PG_HOST
    ):
        raise ConfigException(
            """
            PG_DATABASE
            PG_USER
            PG_PASSWORD
            PG_PORT
            PG_HOST
            env vars must be set
            """
        )


PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_DATABASE = os.getenv("PG_DATABASE")

check_config()
