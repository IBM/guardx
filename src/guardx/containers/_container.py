import io
import json
import logging
import tarfile
from importlib import resources as impresources
from typing import TYPE_CHECKING

import docker
from guardx import sandbox

if TYPE_CHECKING:
    from docker.errors import DockerException


class Container:
    """Internal class to handle container creation and context."""

    def __init__(self, docker_image: str = "lab-validator:latest"):
        """Entry block.

        Args:
        docker_image: docker image name to instantiate
        """
        self.docker_image = docker_image
        self.container = None #NOSONAR

    def start_container(self):
        """Start the container, sleep for infinity and return handle."""
        try:
            client = docker.from_env()
        except docker.errors.DockerException as de:  # type: ignore[attr-defined]
            raise RuntimeError(
                "DockerException when trying to get a docker client for the PythonExecutes validator. \
                    Perhaps you need to run a Docker daemon/podman machine?"
            ) from de
        self.container = client.containers.create(self.docker_image, "sleep infinity", detach=True)
        self.container.start()
        logging.info(f"Container using image {self.docker_image} has now started. Info: {self.container}")

        return self.container

    def put_code(self, python_code, target_file_name='file.py'):
        """Put python_code (str) into the container as a file named target_file_name.

        Args:
        python_code: docker image name to instantiate
        target_file_name: name of file to write inside the container
        """
        if self.container is None:
            raise RuntimeError("Error in put code. Container not started. call .start_container() first")
        # copy the input python code into a docker container.
        tarstream = io.BytesIO()
        with tarfile.open(fileobj=tarstream, mode='w') as sh:
            # Add the input file to the tar archive in file.py
            encoded_python_code = python_code.encode(encoding='utf-8')
            encoded_python_code_tar_info = tarfile.TarInfo(name=target_file_name)
            encoded_python_code_tar_info.size = len(encoded_python_code)
            sh.addfile(
                tarinfo=encoded_python_code_tar_info,
                fileobj=io.BytesIO(encoded_python_code),
            )

        # copy the tarstream in to the docker container.
        tarstream.seek(0)
        self.container.put_archive("/", tarstream)
        return self.container

    def put_file(self, file_name):
        """Put file_name into the container.

        Args:
        file_name: Name of file to be copied into container
        """
        if self.container is None:
            raise RuntimeError("Error in put file. Container not started. call .start_container() first")
        tarstream = io.BytesIO()
        with tarfile.open(fileobj=tarstream, mode='w') as sh:
            sh.add(file_name)
        # copy the tarstream in to the docker container.
        tarstream.seek(0)
        self.container.put_archive("/", tarstream)
        return self.container

    def put_resource(self, file_name):
        """Put library resource file_name into the container.

        Args:
        file_name: Name of file to be copied into container
        """
        if self.container is None:
            raise RuntimeError("Error in put resource. Container not started. call .start_container() first")

        inp_file = impresources.files(sandbox) / file_name

        # copy the input python code into a docker container.
        tarstream = io.BytesIO()
        with tarfile.open(fileobj=tarstream, mode='w') as sh:
            # Add the input file to the tar archive in file.py
            file_tar_info = tarfile.TarInfo(name=file_name)
            file_tar_info.size = inp_file.stat().st_size
            sh.addfile(
                tarinfo=file_tar_info,
                fileobj=inp_file.open('rb'),
            )

        # copy the tarstream in to the docker container.
        tarstream.seek(0)
        self.container.put_archive("/", tarstream)
        return self.container

    def put_json(self, file_name, data):
        """Put JSON data into the container as a file.

        Args:
        file_name: Name of file to be created in container
        data: Dictionary to be serialized as JSON
        """
        if self.container is None:
            raise RuntimeError("Error in put json. Container not started. call .start_container() first")
        
        # Serialize the data to JSON string
        json_str = json.dumps(data)
        encoded_json = json_str.encode(encoding='utf-8')
        
        # Create tar archive with the JSON file
        tarstream = io.BytesIO()
        with tarfile.open(fileobj=tarstream, mode='w') as sh:
            json_tar_info = tarfile.TarInfo(name=file_name)
            json_tar_info.size = len(encoded_json)
            sh.addfile(
                tarinfo=json_tar_info,
                fileobj=io.BytesIO(encoded_json),
            )
        
        # Copy the tarstream into the docker container
        tarstream.seek(0)
        self.container.put_archive("/", tarstream)
        return self.container

