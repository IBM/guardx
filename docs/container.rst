Container runtime support
=========================

We use the Docker API internally for sandbox management. Hence, any container runtime
that is Docker API compatible should work. This includes Podman and Docker on top of Lima.

MacOS
-----

* Podman, the container images are maintained on the host and the Podman containers are run inside the Podman machine (Linux VM). To get GuardX to work, will need to set the env DOCKER_HOST to point to the appropriate UNIX socket used to access the Podman machine. See `this <https://podman-desktop.io/docs/migrating-from-docker/using-the-docker_host-environment-variable>`_ for more details.

  .. code-block:: bash

   podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}'
   export DOCKER_HOST=unix://<your_podman_socket_location>

* Docker on Lima: Run Docker on Lima `yaml <https://github.com/lima-vm/lima/blob/master/templates/docker.yaml>`_. Then set the DOCKER_HOST env to *unix://{{.Dir}}/sock/docker.sock*, where *.Dir* is usually your home directory. The docker images are created inside the Docker environment inside the Lima VM as well as any containers.

* Lima with nerdctl: Not tested, but should in theory work the same way as with Docker on Lima. Find a way to set DOCKER_HOST to point to containerd "server" inside the Lima VM.

* Rancher: Not tested.
