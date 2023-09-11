import re
import textwrap
from functools import lru_cache
from typing import Dict, Type

import libcst as cst
from IPython.core.interactiveshell import InteractiveShell
from marko.block import FencedCode


class Interpreter:
    def __init__(self, interpreter_id: str) -> None:
        self.interpreter_id = interpreter_id


@lru_cache
class Python(Interpreter):
    language = "python"

    def __init__(self, interpreter_id: str) -> None:
        super().__init__(interpreter_id)
        self.shell = InteractiveShell()

    def run(self, code):
        execution_count = self.shell.execution_count

        out = self.shell.run_cell(code)
        out.raise_error()
        self.shell.execution_count += 1

        in_ps1 = f"In [{execution_count}]: "
        out_ps1 = f"Out[{execution_count}]: "

        len_in_ps1 = len(in_ps1)

        if out.success:
            if out.result:
                result = f"\n\n{out_ps1}{out.result}"
            else:
                result = ""
        else:
            result = f"{out_ps1}\n{out.error_in_exec.__repr__()}"

        module = cst.parse_module(code)

        header = module.with_changes(body=[]).code
        body = in_ps1 + textwrap.indent(module.with_changes(header=[]).code.strip(), prefix=" "*len_in_ps1)[len_in_ps1:]


        pattern = r'^```'
        # Replacement string
        replacement = r'\\```'
        # Use re.sub() to replace the matches
        content = re.sub(pattern, replacement,  f"{header}{body}{result}", flags=re.MULTILINE)

        return FencedCode(("python", "", content))


interpreters: Dict[str, Type[Interpreter]] = {
    "python": Python,
}
