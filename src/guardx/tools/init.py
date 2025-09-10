"""Guardx initialization."""
import argparse
import os
import os.path
import subprocess
import logging

import docker

import guardx
import guardx.containers as containers


def run(args):
    """Initialization entrypoint."""
    # parse args
    parser = argparse.ArgumentParser(description="GuardX initialization")
    #parser.add_argument(
    #    "--client", help="Container build client", default="docker", choices=["docker", "podman"], required=False
    #)
    #init_args = parser.parse_args(args)

    logging.getLogger().setLevel(logging.INFO)

    try:
        client = docker.from_env()
    except docker.errors.DockerException as de:
        raise RuntimeError(
            "DockerException when trying to get a docker client for the PythonExecutes validator. \
                Perhaps you need to run a Docker daemon/podman machine? See docs/container.rst"
            ) from de

    prefix = os.path.abspath(containers.__file__)
    _, generator = client.images.build(path=f"{os.path.dirname(prefix)}", \
        dockerfile="Dockerfile.sandbox", tag=f"lab-validator:{guardx.__version__}")
    for chunk in generator:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                logging.info(line)
    _, generator = client.images.build(path=f"{os.path.dirname(prefix)}", \
        dockerfile="Dockerfile.analysis", tag=f"lab-analyzer:{guardx.__version__}")
    for chunk in generator:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                logging.info(line)
