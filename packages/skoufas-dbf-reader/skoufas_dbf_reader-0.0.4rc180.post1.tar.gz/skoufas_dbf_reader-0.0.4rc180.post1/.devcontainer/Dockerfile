ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}
ARG XDG_RUNTIME_DIR=/run/user/1000

RUN python -m pip install --upgrade pip \
    && \
    python3 -m pip install \
    pytest \
    pytest-cov \
    flit \
    pre-commit

COPY .pre-commit-config.yaml .
RUN git init . && pre-commit install-hooks

RUN mkdir -p ${XDG_RUNTIME_DIR}
