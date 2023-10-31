FROM python:3.11-buster
RUN groupadd --gid 5000 authz \
    && useradd --home-dir /home/authz/ --create-home --uid 5000 \
        --gid 5000 --shell /bin/sh --skel /dev/null authz

RUN pip install poetry
WORKDIR /home/authz/git
COPY --chown=authz:authz . .
USER root
RUN chmod 777 /home/authz/git
USER authz
RUN poetry install
ENTRYPOINT ["poetry","run","python","main.py"]
