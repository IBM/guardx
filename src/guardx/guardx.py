"""The package entrypoint."""
import logging
from typing import Dict, Set

import guardx.sandbox.executor as executor
from guardx.analysis import AnalysisResults, AnalysisType, StaticAnalysis
from guardx.config import ConfigLoader
from guardx.sandbox.stypes import ExecutionResults


class Guardx(object):
    """GuardX class exposing the main consumer API."""

    def __init__(self, config: Dict = None, config_path: str = None) -> None:
        """Entry init block for Guardx.

        Args:
          config: the object configuration (takes precedence over configuration file)
          config_path: the configuration file path

        """
        super().__init__()
        self.config = ConfigLoader.load_config(config_path) if config is None else config

    def analyze(self, code: str, analyses: Set[AnalysisType]) -> AnalysisResults:
        """Analyze code using analysis type.

        Args:
          code: the code to be analyzed
          analyses: the types of analysis to be performed

        Returns:
          The analysis results

        """
        static_analysis = StaticAnalysis(code, analyses, self.config)
        return static_analysis.analyze()

    def execute(
        self,
        code: str,
        analysis_results: AnalysisResults = None,
        dryrun: bool = False, #NOSONAR
    ) -> ExecutionResults:
        """Execute code in a sandbox guarded by security policies.

        Args:
          code: the code to be analyzed
          policy: a set defining the policy enforced by the execution sandbox
          analysis_results: a dictionary with the results of a previously executed analysis step
          dryrun: a flag specifying whether the execution should be a dry run or actual execution

        Returns:
          The execution results

        """
        logging.getLogger().setLevel(logging.INFO)
        v = executor.PythonExecutesWithSeccomp(self.config.execution)
        result = v(code)
        return result
