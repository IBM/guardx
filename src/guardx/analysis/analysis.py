"""Define types for the analysis package."""

import json
import logging
from typing import Set

from guardx.analysis.specialization import SpecializationAnalysis, SpecializationAnalysisType
from guardx.analysis.types import AnalysisResults, AnalysisType
from guardx.containers import _container
from guardx.schemas import Config

logger = logging.getLogger(__name__)


class StaticAnalysis(object):
    """Wrapper class for static analyses."""

    def __init__(self, code: str, analyses: Set[AnalysisType], config: Config) -> None:
        """Entry init block for Specialization Analysis.

        Args:
          code: the code to be analyzed
          analyses: the types of analysis to be performed
          config: relevant configurations dictionary
        Exceptions:
          SyntaxError, CalledProcessError

        """
        super().__init__()
        self.code = code
        self.config = config
        self.analyses = analyses
        self.container = None
        self.container_work_dir = "/app"
        self.file_name = "file.py"

    def analyze(self) -> AnalysisResults:
        """Execute static analyses on the input code."""
        # TBD: add thread pool for running analyses concurrently
        results = AnalysisResults()
        if AnalysisType.SPECIALIZATION in self.analyses:
            sa = SpecializationAnalysis(self.code)
            results[AnalysisType.SPECIALIZATION] = {
                SpecializationAnalysisType.FUNCTIONS: sa.get_fn_set(),
                SpecializationAnalysisType.SYSCALLS: sa.get_sc_set(),
                SpecializationAnalysisType.CAPABILITIES: sa.get_capability_set(),
            }
        if AnalysisType.DETECT_SECRET in self.analyses:
            results[AnalysisType.DETECT_SECRET] = self.__detect_secrets()
        if AnalysisType.UNSAFE_CODE in self.analyses:
            results[AnalysisType.UNSAFE_CODE] = self.__detect_unsafe()
        results = self.__summarize_all(results)
        return results

    def __summarize_all(self, results):
        # TODO summarize results
        logging.debug(self.config.analysis)
        return results

    def __summarize_secrets(self, secrets_out, file_name):
        """Format and summarize detect secrets results.

        Args:
          secrets_out: output from detect secrets
          file_name: file that was processed
        """
        if secrets_out.exit_code != 0:
            secrets = "Detect secrets invocation failed in container"
        else:
            result = json.loads(secrets_out.output.decode())
            secrets = result.get("results").get(file_name, None)
        return secrets

    def __summarize_bandit(self, bandit_out):
        """Format and summarize results from bandit.

        Args:
          bandit_out: output from bandit run
        """
        if bandit_out.exit_code != 0:
            unsafe_code = "Bandit invocation failed in container"
        else:
            output = bandit_out.output.decode()
            result = output[output.index("{") :]
            unsafe_code = json.loads(result).get("results", None)
        return unsafe_code

    def __detect_secrets(self):
        """Run detect secrets and summarize results.

        Args:
          file_name: target file name
        """
        container = self.init_runner()
        result = container.exec_run(f"detect-secrets scan {self.container_work_dir} --all-files")

        logger.debug(result)
        return self.__summarize_secrets(result, self.file_name)

    def __detect_unsafe(self):
        """Run bandit and summarize results.

        Args:
          file_name: target file name
        """
        container = self.init_runner()
        result = container.exec_run(f"bandit --exit-zero -f json {self.file_name}", workdir=self.container_work_dir)
        logger.debug(result)
        return self.__summarize_bandit(result)

    def init_runner(self, image_name="lab-analyzer:latest"):
        """Initialize a container, move code into it, summarize results of static analysis.

        Args:
          image_name: container image to instantiate
        """
        if self.container is None:
            c_wrapper = _container.Container(image_name)
            self.container = c_wrapper.start_container()
            c_wrapper.put_code(self.code, f"{self.container_work_dir}/{self.file_name}")
        return self.container
