import re
from pathlib import Path

from marko import Markdown, block
from marko.md_renderer import MarkdownRenderer

from dumas.lib.interpreters import interpreters

FENCED_CODE_LANG_REGEX = re.compile(r"dumas\[(?P<interpreter_name>[\d\w_]+)(@(?P<interpreter_id>[\w\d_-]+))?\]")


class Renderer(MarkdownRenderer):
    def __init__(self):
        super().__init__()

    def render_fenced_code(self, element: block.FencedCode) -> str:
        match = FENCED_CODE_LANG_REGEX.match(element.lang)

        if not match:
            return super().render_fenced_code(element)
        match_dict = match.groupdict()
        interpreter_id = match_dict.get("interpreter_id", "default")
        interpreter_name = match_dict["interpreter_name"]

        interpreter = interpreters[interpreter_name](interpreter_id)

        return self.render(interpreter.run(self.render_raw_text(element.children[0]), **{}))


def render_text(text, *, renderer=Renderer) -> str:
    return Markdown(renderer=renderer)(text)


def render_file(path_to_file: Path, *, renderer=Renderer) -> str:
    return render_text(path_to_file.read_text(), renderer=renderer)