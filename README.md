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

* `logging.`**`create_logger()`**

* `logging.open_logger()`

* *class* `logging.`**`Logger`**

  * `close()`

  * `delete()`

  * `debug()`
  * `info()`
  * `warning()`
  * `error()`
  * `critical()`

  * `get_columns()`

  * `query()`

