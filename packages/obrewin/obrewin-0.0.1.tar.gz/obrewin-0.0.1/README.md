# Obrewin Framework

A quantitative trading framework made for indie trading.

# User Guide

### Dependencies

- Python 3.11+
- Rust 1.72+

### Installation

```bash
pip install obrewin
```

# Developer Guide

Main development is going under WSL 2 Ubuntu 22.04 LTS.

### Construct Python environment

Make your Python virtual environment, then install dependencies by following.

```bash
pip install -r requirements-dev.txt
```

### Build the binary files for Python code

This project uses [`maturin`](https://www.maturin.rs/) to integrate the Rust and Python codes.

```bash
maturin develop
```

### Configure [`pre-commit`](https://pre-commit.com/)

```bash
pre-commit install
```
