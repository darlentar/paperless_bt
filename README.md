# python-quickstart

Just a simple package to bootstrap a python project with pdm.

Steps:
- Rename package name in `pyproject.toml` file
- Remove dummy test `tests/test_dummpy.py` file
- Check everything with `tox`

It uses:
- mypy (for typing)
- pytest (for testing)
- ruff (for formatting/linting)
