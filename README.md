# sqlogging

## Installation

```bash
pip install sqlogging
```

## Usage

```python
from sqlogging import logging

name = "test_logger"
columns = ["iter", "score"]
logger = logging.create_logger(name=name, columns=columns)

logger.info({"iter": 0, "score": .4})
logger.info({"iter": 1, "score": .1})
logger.info({"iter": 2, "score": .8})

result = logger.query(f"SELECT SUM(score) FROM {name}")
print("sum of scores:", result[0][0])
```

## API

### `create_logger()`

### `open_logger()`

### `Logger.close()`

### `Logger.delete()`

### `Logger.debug()`
### `Logger.info()`
### `Logger.warning()`
### `Logger.error()`
### `Logger.critical()`

### `Logger.get_columns()`

### `Logger.query()`

