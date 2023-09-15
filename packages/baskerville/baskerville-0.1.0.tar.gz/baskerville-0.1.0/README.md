<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jaynewey/baskerville/main/static/logo-dark.svg?raw=true" width="50%">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/jaynewey/baskerville/main/static/logo-light.svg?raw=true" width="50%">
    <img src="https://raw.githubusercontent.com/jaynewey/baskerville/main/static/logo-light.svg?raw=true" width="50%">
  </picture>

---

[![PyPI - Version](https://img.shields.io/pypi/v/baskerville)](https://pypi.org/project/baskerville)
[![docs](https://github.com/jaynewey/baskerville-py/actions/workflows/docs.yml/badge.svg)](https://jaynewey.github.io/baskerville-py)
[![GitHub](https://img.shields.io/github/license/jaynewey/baskerville-py)](https://github.com/jaynewey/baskerville-py/blob/main/LICENSE)

Infer and validate data-type schemas in Python.

</div>

## Installation

```
pip install baskerville
```

## Example

```
# mascots.csv
Name,LOC,Species
Ferris,42,Crab
Corro,7,Urchin
```

```python
>>> import baskerville
>>> fields = baskerville.infer_csv("mascots.csv")
>>> print(baskerville.display_fields(fields))
╭──────┬─────────┬─────────╮
│ Name │ LOC     │ Species │
├──────┼─────────┼─────────┤
│ Text │ Integer │ Text    │
│      │ Float   │         │
│      │ Text    │         │
╰──────┴─────────┴─────────╯
```

## Contributing

<!-- TODO: add "pre-commit checklist" when CI is set up -->

### Versioning

The repo bases versioning from [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
