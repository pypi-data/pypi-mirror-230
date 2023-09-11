import re
import textwrap
from functools import lru_cache
from typing import Dict, Type

import libcst as cst
from IPython.core.interactiveshell import InteractiveShell
from marko.block import FencedCode

from black import format_str, Mode as black_Mode



class Interpreter:
    def __init__(self, interpreter_id: str) -> None:
        self.interpreter_id = interpreter_id


@lru_cache
class Python(Interpreter):
    language = "python"

    def __init__(self, interpreter_id: str) -> None:
        super().__init__(interpreter_id)
        self.shell = InteractiveShell()


    def run(self, code, black: bool = True):
        execution_count = self.shell.execution_count

        out = self.shell.run_cell(code)
        out.raise_error()
        self.shell.execution_count += 1

        in_ps1 = f"In [{execution_count}]: "
        len_in_ps1 = len(in_ps1)
        indent_ps1 = " " * (len_in_ps1 - (1 + 3 + 1)) + "...: "

        out_ps1 = f"Out[{execution_count}]: "

        if out.success:
            if out.result:
                result = f"\n\n{out_ps1}{out.result}"
            else:
                result = ""
        else:
            result = f"{out_ps1}\n{out.error_in_exec.__repr__()}"

        module = cst.parse_module(code)

        header = module.with_changes(body=[]).code
        body = module.with_changes(header=[]).code.strip()
        if black:
            body = format_str(body, mode=black_Mode())

        render_body = in_ps1 + textwrap.indent(body, prefix=indent_ps1, predicate=lambda n: True)[len_in_ps1:]

        pattern = r"^```"
        # Replacement string
        replacement = r"\\```"
        # Use re.sub() to replace the matches
        content = re.sub(pattern, replacement, f"{header}{render_body}{result}", flags=re.MULTILINE)

        return FencedCode(("python", "", content))


interpreters: Dict[str, Type[Interpreter]] = {
    "python": Python,
}
