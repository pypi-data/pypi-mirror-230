# Requirement Compare

A CLI that generate a version changelog based on git history and local requirement file.

## Installation

```bash
pip install --upgrade pip
pip install requirement-compare
```

## Usage

```bash
$ requirement-compare requirements.txt
- Added `last_package` version `1.0.0`
- Bump `example_package` from `1.0.0` to `2.0.0`
- Removed `another_package` version `1.0.0`
```
