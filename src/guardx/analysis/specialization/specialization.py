"""Code analysis for ELF binaries."""
import ast
import logging
import subprocess
from typing import List, Set

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

from guardx.analysis.specialization.capabilities import map_sc_capabilities
from guardx.analysis.specialization.x86_64_tables import map_stdlib_sc

SC_LIST = "/app/src/guardx/analysis/specialization/scripts/sc_list"
STDLIB_PATTERN = ["seq_", "@GLIBC"]


class SpecializationAnalysis:
    """Specialization analysis.

    Finds the minimum sets of functions, system calls,
    and capabilities required by a given program.
    """

    def __init__(self, code: str) -> None:
        """Entry init block for Specialization Analysis.

        Args:
          code: the code to be analyzed

        Exceptions:
          SyntaxError, CalledProcessError

        """
        super().__init__()
        self.code = code
        self.__check_code_syntax()
        self.functions = self.__analyze()

    def __check_code_syntax(self):
        """Validate the code syntax."""
        try:
            ast.parse(self.code)
        except SyntaxError as err:
            logging.error(f"Invalid input code {repr(self.code)}: {err}")
            raise SyntaxError(f"Invalid input: {repr(self.code)}. This is not a valid Python code.") from err

    def __analyze(self, pattern: List[str] = None) -> Set:
        logging.debug(f"Compiling input code: {repr(self.code)}")
        try:
            result = subprocess.run([SC_LIST, self.code], capture_output=True, shell=False, text=True, check=True)
        except subprocess.CalledProcessError as err:
            logging.error(f"Unable to compile code.\nCommand: {err.cmd}\nReturn Code: {err.returncode}")
            raise
        filename = result.stdout.strip("\n")
        logging.info(f"Compiled native code path: {filename}")
        with open(filename, 'rb') as f:
            elffile = ELFFile(f)
            return self.read_symbol_table_functions(elffile, pattern)

    def read_symbol_table_functions(self, elffile, pattern: List[str] = None) -> Set:
        """Display the functions found in the symbol tables contained in the file."""
        symbol_tables = [(idx, s) for idx, s in enumerate(elffile.iter_sections()) if isinstance(s, SymbolTableSection)]

        if not symbol_tables and elffile.num_sections() == 0:
            logging.debug("Dynamic symbol information is not available for displaying symbols.")

        sl = []
        for _, section in symbol_tables:
            if not isinstance(section, SymbolTableSection):
                continue
            sl.extend([symbol.name for symbol in section.iter_symbols() if symbol['st_info']['type'] == 'STT_FUNC'])
        if pattern:
            sl = filter(lambda e: any(i in e for i in pattern), sl)
        return set(sl)

    def get_fn_set(self, pattern: List[str] = STDLIB_PATTERN) -> Set:
        """Return the function set invoked by the program."""
        return self.functions

    def get_sc_set(self) -> Set:
        """Return the system call set invoked by the program."""
        sl = list(map(map_stdlib_sc, self.get_fn_set()))
        return set().union(*sl)

    @staticmethod
    def get_capability_set(self) -> Set:
        """Return the capability set required by the program."""
        cl = {frozenset(map_sc_capabilities(sc)) for sc in self.get_sc_set()}
        return set().union(*cl)
