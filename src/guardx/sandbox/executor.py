"""Secure code execution facilities."""
import logging
import re

import guardx
from guardx.containers import _container
from guardx.sandbox.stypes import ExecutionResults
from guardx.schemas import Execution

logger = logging.getLogger(__name__)


class PythonExecutesWithSeccomp:
    """A Python code executor that enforces a seccomp profile."""

    def __init__(self, config: Execution):
        """Constructor.

        Args:
            config: Configuration of executor

        """
        # TODO make it a parameter whether we re-create the container each time
        # or re-use the existing one. If re-use, use context manager.
        self.config = config
        if self.config.docker_image is None:
            self.config.docker_image = f"lab-validator:{guardx.__version__}"
        self.c_wrapper = _container.Container(self.config.docker_image)

    def __call__(self, code: str) -> ExecutionResults:
        """Execute code as a container under the specified policy.

        Args:
            code: code to be executed.

        Returns:
            Execution results.

        """
        # TODO other ones return bool. what to do?
        container = self.c_wrapper.start_container()
        self.c_wrapper.put_code(code)
        # Add the runner harness to the tar archive in runner.py
        # harness_tar_info = tarfile.TarInfo(name='runner.py')
        # harness_tar_info.size = len(_ENCODED_RUNNER_HARNESS)
        # sh.addfile(tarinfo=harness_tar_info, fileobj=io.BytesIO(_ENCODED_RUNNER_HARNESS))
        self.c_wrapper.put_resource('docker_seccomp_default.json')
        self.c_wrapper.put_resource('_executor.py')

        # run the code in a containerized environment. Try 3 times.
        # TODO Kill the code if it takes too long.
        tries = 0
        while tries < 3:
            logger.info(f"Attempting to run code in the Python container (attempt {tries+1}/3)")
            tries += 1
            result = container.exec_run("python3 _executor.py " + self.config.policy_seccomp)
            result_output_decoded = result.output.decode()
            if result.exit_code == 0:
                logger.info(
                    f"Exit code: {result.exit_code}. Killing container and attempting to format the execution result."
                )
                container.kill()
                return ExecutionResults(result)
            elif "ModuleNotFoundError" in result_output_decoded:
                # Try to resolve ModuleNotFoundError by extracting the name of the
                # missing import and then installing it.
                logger.info(
                    f"Exit code: {result.exit_code}. There appears to be a missing import. \
                        STDOUT:\n{result_output_decoded}."
                )
                match = re.search(r"No module named '(.*)'", result_output_decoded)
                assert (
                    match
                ), f"Expected to find the string 'No module named', but did not. STDOUT:\n{result_output_decoded}."
                assert (
                    len(match.groups()) > 0
                ), f"Expected to find the string 'No module named' AND a grouping, but did not find grouping. \
                    The STDOUT was:\n{result_output_decoded}."
                package_name = match.groups()[0]
                # Apply manual import->package rules.
                if package_name == 'torch':
                    package_name = "torchvision"
                elif package_name == 'yaml':
                    package_name = 'pyyaml'
                logger.info(
                    f"Attempting to resolve a missing import using pip. Missing import was: {package_name}. \
                        We might have translated this package from the module name."
                )
                container.exec_run(f"pip3 install {package_name}")
            else:
                logger.info(
                    f"The Python call failed for a reason we don't know how to handle. \
                        We are going to try again, even though the code and environment hasn't changed. \
                        Output was:\n{result_output_decoded}"
                )
        container.kill()
        assert result.exit_code != 0
        return ExecutionResults(result)
