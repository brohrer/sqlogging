# sqlogging

A logger that is based on Python's
[sqlite3](https://docs.python.org/3/library/sqlite3.html)
library. Log entries are stored in a sqlite table and can be accessed
with SQL queries.
It is inspired by the [logging](https://docs.python.org/3/library/logging.html)
library, but does not stay strictly faithful to the API. 

## Installation

```bash
pip install sqlogging
```

## Usage

```python
from sqlogging import logging


logger = logging.create_logger(name="test_logger", columns=["iter", "score"])
logger.info({"iter": 0, "score": .4})
logger.info({"iter": 1, "score": .1})
logger.info({"iter": 2, "score": .8})

result = logger.query(f"SELECT SUM(score) FROM {logger.name}")
print("sum of scores:", result[0][0])

logger.delete()
```

## API

### `create_logger()`
`logging.create_logger(name="log", dir_name=".", level="info", columns=["ts", "data"])`

For creating a new Logger from scratch. If you try to open a Logger by the same name
as a pre-existing logger you'll get a `sqlite3.OperationalError`.

* Parameters
  * `name`(`str`) - The name of the Logger. This will be both the name of the
  name of the table and the name of the sqlite3 database file (`<name>.db`).
  * `dir_name`(`str`) - The directory in which the database file will be stored.
  If it doesn't already exist, it will be created.
  * `level`(`str`) - The logging severity level.
  Must be one of `{'debug', 'info', 'warning', 'error', 'critical'}` (case insensitive).
  Only log messages of equal or higher severity will be processed.
  * `columns`(`List` of `str`) - The names of the columns to be created in the
  sqlite database.
* Return type: `Logger`
* Raises:
  * `ValueError`: If `level` is not one of the 5 allowed levels.

### `open_logger()`
`logging.open_logger(name="log", dir_name="logs")`

For re-opening an existing Logger.

* Parameters: as in `create_logger()`
* Return type: `Logger`

### `Logger`
*class* `logging.Logger(name, dir_name, level=None, columns=None, create=True)`
* Parameters: as in `create_logger()`
  * `create`(`bool`) - Whether a new Logger should be created or an existing
  one re-opened.

#### `close()`
Close the connection to the logger database. Can be reopened later with
`logging.open_logger()`.

#### `delete()`
Close the connection to the database and delete the database file.
Remove it from existence. 

#### `debug(data)` \\ `info(data)` \\ `warning(data)` \\ `error(data)` \\ `critical(data)`

* Parameters
  * `data`(`dict`) - Write (at the specified severity level) a row into the sqlite db.
  The dictionary contains keys with the name of the column to be written, and
  values with the data element corresponding to that columns.

  Any columns not included
  in the dict keys will be populated with `NULL`. (These will be `None` when
  queried and converted to Python.)

#### `get_columns()`
Returns a list of all column names.
* Return type: `list` of `str`

#### `query(query_str)`
Run a SQL query against the logger database. Here's a reference for the
[particular dialect of SQL](https://www.sqlite.org/lang.html). It's
mostly standard stuff, but as with all SQL dialects can have some surprises,
especially if you use some of the fancier features.
* Parameters:
  * `query_str` (`str`)
* Return type: `list` of `tuple`
