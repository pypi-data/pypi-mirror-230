# SPDX-FileCopyrightText: 2023-present Alvaro Leiva Geisse <aleivag@gmail.com>
#
# SPDX-License-Identifier: MIT
import sys
from pathlib import Path
from typing import Optional

import click

from dumas.__about__ import __version__
from dumas.lib import renderer


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="dumas")
def dumas():
    ...


@dumas.command()
@click.option("--output-file", metavar="OUTPUT_FILE", type=click.File(mode="w"), help="Output file", default="-")
@click.argument("input_file", type=Path)
def render_file(input_file: Path, output_file):
    """
    writes [INPUT FILE] into --out file
    """

    output_file.write(renderer.render_file(input_file))


@dumas.command()
@click.option(
    "--check/--execute",
    "check",
    default=False,
    help="execute (a.k.a do the rendering) or check (fail if there is need for rendering)",
)
@click.option("--output-dir", metavar="OUTPUT_DIR", type=Path, required=True, help="Output file")
@click.argument("input_dir", type=Path)
def render_dir(input_dir: Path, output_dir: Path, check: bool):
    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()

    for f in input_dir.glob("**/*.md"):
        output_text = renderer.render_file(f)
        finalf = output_dir / f.relative_to(input_dir)
        if check:
            if finalf.read_text() != output_text:
                click.echo(f"file {f} needs to be renderer", err=True)
                sys.exit(-1)
        else:
            finalf.write_text(output_text)

    if check:
        click.echo("No changes needed", err=True)
