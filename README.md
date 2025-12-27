# tdom-svcs

TDOM integration with svcs dependency injection.

## Installation

```bash
$ uv add tdom-svcs
```

Or using pip:

```bash
$ pip install tdom-svcs
```

## Requirements

- **svcs**
- **Python 3.14+** (uses PEP 695 generics and modern type parameter syntax)

## Overview

This package provides integration between TDOM (Template DOM) and the svcs dependency injection library.

## Testing

```bash
# Run tests
pytest

# Run tests in parallel
pytest -n auto

# Run with coverage
pytest --cov=tdom_svcs
```
