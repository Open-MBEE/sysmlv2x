# sysmlv2x

This repository provide a SysIDE based library to serialize SysMLv2 textual notatation as file or string so, it can
be transformed and executed with an SCXML engine.

Look at examples/basic_notebook.ipynb for how to use the API with the simpleSM.sysml model.

It uses [SCXML Python interpreter][https://github.com/Open-MBEE/scxml4py] to interpret SCXML models


## Installation

```bash
pip install .

Check requirements.txt for dependencies

## Installation

This package depends on [SCXML Python interpreter](https://github.com/Open-MBEE/scxml4py), which is **not available on PyPI** and must be installed directly from GitHub.

It also depends on sysIDE automator library: https://sensmetry.com/syside/

### Recommended install (development or production):

```bash
pip install syside-license syside --index-url https://gitlab.com/api/v4/projects/69960816/packages/pypi/simple --upgrade
pip install -e .
