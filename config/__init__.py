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


PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_DATABASE = os.getenv("POSTGRES_DB")

check_config()
