# Python Logging (beans_logging)

Loguru based custom logging package (beans_logging) for python projects.

## Features

* Loguru based logging - [https://pypi.org/project/loguru](https://pypi.org/project/loguru)
* Custom basic logging module
* Logging to files (all, error, json)
* Custom logging formats
* Custom options as a config
* Colorful logging
* Multiprocess compatibility (Linux, macOS - 'fork', Windows - 'spawn')

---

## Installation

### 1. Prerequisites

* **Python (>= v3.7)**
* **PyPi (>= v21)**

### 2. Install beans-logging

#### A. [RECOMMENDED] PyPi install

```sh
# Install or upgrade beans-logging package:
pip install --upgrade beans-logging

# To uninstall package:
pip uninstall -y beans-logging
```

#### B. Manually add to PYTHONPATH (Recommended for development)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/python_logging.git beans_logging
cd beans_logging

# Install python dependencies:
pip install --upgrade pip
cat requirements.txt | xargs -n 1 -L 1 pip install --no-cache-dir

# Add current path to PYTHONPATH:
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

#### C. Manually compile and setup (Not recommended)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/python_logging.git beans_logging
cd beans_logging

# Building python package:
pip install --upgrade pip setuptools wheel
python setup.py build
# Install python dependencies with built package to current python environment:
python setup.py install --record installed_files.txt

# To remove only installed beans-logging package:
head -n 1 installed_files.txt | xargs rm -vrf
# Or to remove all installed files and packages:
cat installed_files.txt | xargs rm -vrf
```

### 3. Configuration (You can skip this step, if you don't want to configure)

* First, check **.env.example (environment variables)** file.
* Sample **.env.example** file - [https://github.com/bybatkhuu/python_logging/blob/main/.env.example](https://github.com/bybatkhuu/python_logging/blob/main/.env.example)
* Copy **.env.example** file to **.env** and change environment variables:

```sh
cp -v .env.example [PROJECT_DIR]/.env
cd [PROJECT_DIR]
vi .env
```

* Make **configs** directory inside project's base directory and copy **configs/logger.yml** file into **configs**.
* Sample **logger.yml** config file - [https://github.com/bybatkhuu/python_logging/blob/main/configs/logger.yml](https://github.com/bybatkhuu/python_logging/blob/main/configs/logger.yml)
* Then edit variable options:

```sh
mkdir -vp [PROJECT_DIR]/configs

cp -v logger.yml [PROJECT_DIR]/configs/logger.yml
rm -vf logger.yml
cd [PROJECT_DIR]
vi configs/logger.yml
```

## Usage/Examples

### Simple example

**sample.py**:

```python
from beans_logging import logger

logger.info('Logging info.')
logger.success('Success.')
logger.warning('Warning something.')
logger.error('Error occured.')
logger.critical('CRITICAL ERROR.')


def divide(a, b):
    _result = a / b
    return _result

try:
    divide(10, 0)
except Exception as err:
    logger.exception("Failed to divide:")
```

### Advanced example

**configs/logger.yml**:

```yml
logger:
    level: "TRACE"
    use_color: true
    use_icon: false
    use_backtrace: true
    std_format_str: "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{lvlname:<5}</level> | <w>{file}</w>:<w>{line}</w>]: <level>{message}</level>"
    use_log_file: true
    logs_dir: ./logs
    file_format_str: "[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {lvlname:<5} | {file}:{line}]: {message}"
    rotate_when:
        at_hour: 0
        at_minute: 0
        at_second: 0
    rotate_file_size: 10000000  # 10MB
    backup_file_count: 50
    file_encoding: utf8
    all_log_filename: "{app_name}.std.all.log"
    err_log_filename: "{app_name}.std.err.log"
    use_log_json: true
    use_custom_json: true
    json_all_log_filename: "{app_name}.json.all.log"
    json_err_log_filename: "{app_name}.json.err.log"
```

**.env**:

```sh
ENV=development
DEBUG=true

APP_NAME=app
PY_LOGS_DIR="./logs"
```

**main.py**:

```python
from beans_logging import logger

logger.trace('Tracing...')
logger.debug('Debugging...')
logger.info('Logging info.')
logger.success('Success.')
logger.warning('Warning something.')
logger.error('Error occured.')
logger.critical('CRITICAL ERROR.')


def divide(a, b):
    _result = a / b
    return _result

def nested(c):
    try:
        divide(5, c)
    except ZeroDivisionError:
        logger.exception("Show me, what value is wrong:")

nested(0)
```

---

## Running Tests

To run tests, run the following command:

```sh
python -m unittest tests/test_*.py
```

## Environment Variables

You can use the following environment variables inside **.env** file:

```sh
ENV=development
DEBUG=true
APP_NAME=app
PY_LOGS_DIR="/var/log/app"
```

## Configuration

You can use the following sample configuration:

```yaml
logger:
    level: "INFO"
    use_color: true
    use_icon: false
    use_backtrace: true
    std_format_str: "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{lvlname:<5}</level> | <w>{file}</w>:<w>{line}</w>]: <level>{message}</level>"
    use_log_file: false
    logs_dir: ./logs
    file_format_str: "[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {lvlname:<5} | {file}:{line}]: {message}"
    rotate_when:
        at_hour: 0
        at_minute: 0
        at_second: 0
    rotate_file_size: 10000000  # 10MB
    backup_file_count: 50
    file_encoding: utf8
    all_log_filename: "{app_name}.std.all.log"
    err_log_filename: "{app_name}.std.err.log"
    use_log_json: false
    use_custom_json: false
    json_all_log_filename: "{app_name}.json.all.log"
    json_err_log_filename: "{app_name}.json.err.log"
```

---

## References

* [https://github.com/Delgan/loguru](https://github.com/Delgan/loguru)
* [https://loguru.readthedocs.io/en/stable/api/logger.html](https://loguru.readthedocs.io/en/stable/api/logger.html)
