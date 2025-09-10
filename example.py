import guardx
import guardx.analysis
import guardx.analysis.types
from guardx.analysis.types import AnalysisType
import guardx.policy

import io
import json
import logging
import re
import tarfile
from typing import Optional, TypedDict, Set

import docker

class ExecutionResult(TypedDict):
    success: bool
    result: Optional[str]
    locals: Optional[str]
    stdout: Optional[str]
    docker_exec_result: docker.models.containers.ExecResult

class PythonExecutes:
    def __init__(self):
        """TODO make it a parameter whether we re-create the container each time or re-use the existing one. If re-use, use context manager."""
        pass

    def __call__(
        self, python_code: str,
    ) -> ExecutionResult:  # TODO other ones return bool. what to do?

        # static analysis
        # g = guardx.Guardx()
        # result = g.analyze(python_code, [analysistype])

        # prefilter based on result

        # sandboxed execution
        result = guardx.Guardx().execute(python_code).get_docker_result()
        if result.exit_code == 0:
            return self._format_result(result)
        else:
            return {
                "success": False,
                "result": None,
                "locals": None,
                "stdout": None,
                "docker_exec_result": result,
            }

    def analyze(self, python_code: str) -> guardx.analysis.types.AnalysisResults:

        result = guardx.Guardx().analyze(python_code, {AnalysisType.DETECT_SECRET, AnalysisType.UNSAFE_CODE})
        print(result)

    def _format_result(
        self, docker_result: docker.models.containers.ExecResult
    ) -> ExecutionResult:
        """Formats the result from the wrapper script.

        The output from the wrapper script should look something like:
        ```
        lines of stdout
        -- THIS LINE IS METADATA --
        JSON encoding of {result: "...", locals: {...}}
        ```
        where 'result' is the result of `eval`ing the last line.
        We return the JSON that is returned by the wrapper, with a couple of modifications:
        1. we add an "stdout" that contains the stdout.
        2. if the `result` is None, then we set `result` to the last non-whitespace line of stdout before the meta separator line.
        """
        assert (
            docker_result.exit_code == 0
        ), f"Expected to receive an ExecResult is a successful error code, but got: {docker_result}"

        # Parse the JSON and STDOUT from the result.
        lines = docker_result.output.decode().strip().splitlines()
        json_from_eval_wrapper = json.loads(lines[-1])
        stdout = lines[0 : lines.index("-- THIS LINE IS METADATA --")]

        # The json_from_eval_wrapper has a result key. That result might be None if the last thing that the script did was print something out.
        # In that case, we want the last printed line in STDOUT that wasn't empty to be reported as the result.
        if json_from_eval_wrapper["result"] is None:
            # find the first line in stdout that isn't whitespace.
            non_whitespace_lines = list(
                filter(lambda line: line.strip() != "", stdout.strip().splitlines())
            )
            # If there is such a line, set the result to that line's contents.
            if len(non_whitespace_lines) != 0:
                json_from_eval_wrapper["result"] = non_whitespace_lines[-1]

        return {
            "success": True,
            "result": json_from_eval_wrapper["result"],
            "locals": json_from_eval_wrapper["locals"],
            "stdout": stdout,
            "docker_exec_result": docker_result,
        }


if __name__ == "__main__":
    import argparse

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--file", required=True)
    argument_parser.add_argument("--analyze", action=argparse.BooleanOptionalAction)
    args = argument_parser.parse_args()

    contents = open(args.file).read()

    logging.getLogger().setLevel(logging.INFO)
    v = PythonExecutes()
    if args.analyze:
        result = v.analyze(contents)
    result = v(contents)
    if result["success"]:
        print(result["result"])
        print("SUCCESS")
    else:
        print(result["docker_exec_result"])
        print("DID NOT SUCCEED")
