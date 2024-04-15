# sqlogging

## Installation

```bash
pip install sqlogging
```

## Usage

```python
from sqlogging import logging

name = "test_logger"
dir_name = "."
columns = ["iter", "score"]
logger = logging.create_logger(name=name, dir_name=dir_name, columns=columns)

logger.info({"iter": 0, "score": .4})
logger.info({"iter": 1, "score": .1})
logger.info({"iter": 2, "score": .8})

result = logger.query(f"SELECT SUM(score) FROM {name}")
print("sum of scores:", result[0][0])

logger.delete()
```

## API

### `create_logger()`
`logging.create_logger(name="log", dir_name="logs", level="info", columns=["ts", "data"])`
* Parameters
  * d
* Return type: Logger
* Raises
  * k 

### `open_logger()`
`logging.open_logger(name="log", dir_name="logs")`

### `Logger`
*class* `logging.Logger(name, dir_name, level=None, columns=None, create=True)`

#### `close()'

#### `delete()`

#### `debug(data)`
#### `info(data)`
#### `warning(data)`
#### `error(data)`
#### `critical(data)`

* Parameters
  * data (dict)
* Return type: Logger
* Raises
  * k 

#### `get_columns()`

#### `query(query_str)`

