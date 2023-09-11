# dumas

[![PyPI - Version](https://img.shields.io/pypi/v/dumas.svg)](https://pypi.org/project/dumas)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dumas.svg)](https://pypi.org/project/dumas)

* * *

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install dumas
```

## Using it (shell)

## Using it (api)

You could use `dumas` as part of your own workflow/program

```python
# First import the render functions


In [1]: from dumas.lib.renderer import render_text, render_file
        import textwrap

        MD_TEXT = textwrap.dedent("""
            This is a regular MD
            ====================
    
            with some `funny text` and some text
    
            ```dumas[python@readme]
            x = 1+1
    
            x**2
    
            ```
        """)
```

```python

In [2]: MD_TEXT

Out[2]: 
This is a regular MD
====================

with some `funny text` and some text

\```dumas[python@readme]
x = 1+1

x**2

\```
```

```python

In [3]: render_text(MD_TEXT)

Out[3]: 
# This is a regular MD

with some `funny text` and some text

\```python

In [1]: x = 1+1

        x**2

Out[1]: 4
\```
```

## License

`dumas` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
