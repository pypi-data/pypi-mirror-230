[![codecov](https://codecov.io/gh/rmargar/pymavlog/branch/main/graph/badge.svg?token=0APOFRD0BT)](https://codecov.io/gh/rmargar/pymavlog)
![test](https://github.com/rmargar/pymavlog/actions/workflows/test.yaml/badge.svg)
[![PyPI version](https://badge.fury.io/py/pymavlog.svg)](https://badge.fury.io/py/pymavlog)

# pymavlog

A lightweight python library to parse log files from ArduPilot vehicles based on the [MavLink](https://mavlink.io/) protocol. It is built on top of [pymavlink](https://github.com/ArduPilot/pymavlink) and uses [NumPy](https://numpy.org/) under the hood to vectorize messages.

## Installation

Installation with pip:

```bash
pip install pymavlog
```

or via Poetry

```bash
poetry add pymavlog
```

## Development

Install the package in editable mode:

```bash
pip install -e .
```

Pymavlog is built using [Poetry](https://github.com/python-poetry/poetry), so make sure to have it in your local development environment

```bash
pip install poetry
```

Lastly, install the pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

## Testing

```bash
poetry run pytest tests --cov pymavlog
```

or

```bash
make tests
```

## Usage

Mavlink log files are parsed using `MavLog`, which iterates through the logged messages and saves them in-memory as NumPy arrays. You can parse a file like:

```python
from pymavlog import MavLog


filepath = "foo/bar.bin"
mavlog = MavLog("foo/bar.bin")
mavlog.parse()
```

and access the messages like:

```python
imu_messages = mavlog.get("IMU")
```

and do some calculations, for example calculating the average value:

```python
avg_gyr_x = imu_messages["GyrX"].mean()
```

alternatively, you can access a specific attribute like:

```python
gyr_y = mavlog["IMU"]["Gyrx"]
```

Pymavlog also supports telemetry log files. You can read a tlog file `.tlog` in a similar way as binary log files, like:

```python
from pymavlog import MavTLog


filepath = "foo/bar.tlog"
tlog = MavTLog("foo/bar.tlog")
tlog.parse()
```
