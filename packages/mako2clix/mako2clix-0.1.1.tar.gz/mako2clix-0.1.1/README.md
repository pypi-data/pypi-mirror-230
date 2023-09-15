[![Tests](https://github.com/leaningdiggers/mako2clix/workflows/Tests/badge.svg)](https://github.com/leaningdiggers/mako2clix/actions?workflow=Tests)
[![Codecov](https://codecov.io/gh/leaningdiggers/mako2clix/branch/master/graph/badge.svg)](https://codecov.io/gh/leaningdiggers/mako2clix)
[![PyPI](https://img.shields.io/pypi/v/mako2clix.svg)](https://pypi.org/project/mako2clix/)
[![Read the Docs](https://readthedocs.org/projects/mako2clix/badge/)](https://mako2clix.readthedocs.io/)

# mako2clix

This project aims to port Mako Template to a simple usage on command line

## Installation

To install the mako2clix Python project,
run this command in your terminal:

```
$ pip install mako2clix
```

## Example

Create a file `template.mako` containing:

```mako
hello ${name}!
```

And a data file `data.yaml`:

```yaml
name: world
```

Now you can render the file with:

```bash
$ m2cli -t template.mako -d data.yaml -o rendered
```

The output is saved to `rendered`:

```
hello world!
```

That's all!
