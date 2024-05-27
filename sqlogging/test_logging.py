import os
import shutil
import sqlite3
import time
from sqlogging import logging

TMP_LOGGER_DIR = f"test_logger_{int(time.time())}_dir"


def teardown_logger(logger):
    logger.delete()
    del logger


def teardown():
    shutil.rmtree(TMP_LOGGER_DIR)


def test_logging_dir_creation():
    logger_name = "logging_dir_creation"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=TMP_LOGGER_DIR,
    )
    assert logger.name == logger_name
    assert logger.dir_name == TMP_LOGGER_DIR
    assert logger.db_path == os.path.join(TMP_LOGGER_DIR, logger_name + ".db")
    assert os.path.isdir(TMP_LOGGER_DIR)

    teardown_logger(logger)


def test_levels():
    assert logging.DEBUG == 10
    assert logging.INFO == 20
    assert logging.WARNING == 30
    assert logging.ERROR == 40
    assert logging.CRITICAL == 50


def test_level_setting():
    logger = logging.create_logger(
        name="level_setting",
        level="debug",
        dir_name=TMP_LOGGER_DIR,
    )
    assert logger.level == logging.DEBUG

    teardown_logger(logger)


def test_level_validation():
    try:
        logger = logging.create_logger(
            name="level_validation",
            level="circuital",
            dir_name=TMP_LOGGER_DIR,
        )
        assert False
        teardown_logger(logger)
    except ValueError:
        assert True

def test_default_columns():
    logger = logging.create_logger(
        name="default_columns",
        level="debug",
        dir_name=TMP_LOGGER_DIR,
    )
    table_info = logger.query(f"PRAGMA table_info({logger.name});")
    columns = []
    for row in table_info:
        columns.append(row[1])
    assert len(columns) == 2
    assert "ts" in columns
    assert "data" in columns

    teardown_logger(logger)


def test_column_assignment():
    columns_init = ["time", "iteration", "d3_score", "ABC", "B02349"]
    logger = logging.create_logger(
        name="columns_assignment",
        level="debug",
        dir_name=TMP_LOGGER_DIR,
        columns=columns_init,
    )
    table_info = logger.query(f"PRAGMA table_info({logger.name});")
    columns = []
    for row in table_info:
        columns.append(row[1])
    assert len(columns) == 5
    for col in columns_init:
        assert col in columns

    teardown_logger(logger)


def test_log_delete():
    logger = logging.create_logger(
        name="log_delete",
        dir_name=TMP_LOGGER_DIR,
    )
    table_info = logger.query(f"PRAGMA table_info({logger.name});")
    assert len(table_info) == 2

    logger.delete()
    try:
        table_info = logger.query(f"PRAGMA table_info({logger.name});")
        assert False
    except sqlite3.ProgrammingError:
        assert True

    del logger


def test_log_close():
    logger = logging.create_logger(
        name="log_close",
        dir_name=TMP_LOGGER_DIR,
    )
    table_info = logger.query(f"PRAGMA table_info({logger.name});")
    assert len(table_info) == 2

    logger.close()
    try:
        table_info = logger.query(f"PRAGMA table_info({logger.name});")
        assert False
    except sqlite3.ProgrammingError:
        assert True

    del logger


def test_log_reopen():
    logger_name = "log_reopen"
    columns_init = ["time", "iteration", "d3_score", "ABC", "B02349"]
    logger = logging.create_logger(
        name=logger_name,
        dir_name=TMP_LOGGER_DIR,
        columns=columns_init,
    )
    table_info = logger.query(f"PRAGMA table_info({logger.name});")
    assert len(table_info) == 5

    logger.close()

    try:
        logger = logging.create_logger(
            name=logger_name,
            dir_name=TMP_LOGGER_DIR,
        )
        assert False
    except sqlite3.OperationalError:
        assert True

    logger = logging.open_logger(
        name=logger_name,
        dir_name=TMP_LOGGER_DIR,
    )
    table_info = logger.query(f"PRAGMA table_info({logger.name});")
    assert len(table_info) == 5

    teardown_logger(logger)


def test_open_nonexistent_log():
    logger_name = "nonexistent_log"

    allowed = True
    try:
        logger = logging.open_logger(
            name=logger_name,
            dir_name=TMP_LOGGER_DIR,
        )
        teardown_logger(logger)
    except sqlite3.OperationalError:
        allowed = False

    assert allowed == False


def test_writing_debug():
    logger = logging.create_logger(
        name="writing_debug",
        dir_name=TMP_LOGGER_DIR,
    )
    logger.info({"ts": 23874.2234, "data": "flurpy"})
    result = logger.query(f"SELECT * FROM {logger.name};")
    assert len(result) == 1
    assert result[0][0] == 23874.2234
    assert result[0][1] == "flurpy"

    columns = logger.get_columns()
    assert columns[0] == "ts"
    assert columns[1] == "data"

    teardown_logger(logger)


def test_writing_below_severity():
    logger = logging.create_logger(
        name="writing_below_severity",
        dir_name=TMP_LOGGER_DIR,
        level="warning",
    )
    logger.debug({"ts": 42, "data": "bing bang"})
    result = logger.query(f"SELECT * FROM {logger.name};")
    assert len(result) == 0

    teardown_logger(logger)


def test_writing_above_severity():
    logger = logging.create_logger(
        name="writing_above_severity",
        dir_name=TMP_LOGGER_DIR,
        level="debug",
    )
    logger.critical({"ts": 100000000, "data": "mayhem!"})
    logger.error({"ts": -999, "data": "badness occurred"})
    result = logger.query(f"SELECT * FROM {logger.name};")
    assert len(result) == 2

    teardown_logger(logger)


def test_writing_partial_rows():
    columns_init = ["timestamp", "iteration", "d3_score"]
    logger = logging.create_logger(
        name="writing_partial_rows",
        dir_name=TMP_LOGGER_DIR,
        level="warning",
        columns=columns_init,
    )
    logger.warning({"timestamp": 1234, "iteration": "mayhem!"})
    logger.warning({"timestamp": 9873, "d3_score": "57"})
    logger.error({"iteration": 3, "d3_score": "-.004"})
    result = logger.query(f"SELECT * FROM {logger.name};")
    assert len(result) == 3
    assert result[0][2] is None
    assert result[1][1] is None
    assert result[2][0] is None

    teardown_logger(logger)


def test_writing_nonexistent_column():
    logger = logging.create_logger(
        name="writing_nonexistent_columns",
        dir_name=TMP_LOGGER_DIR,
    )
    try:
        logger.critical({"iteration": 398})
        assert False
    except KeyError:
        assert True

    teardown_logger(logger)


def test_retrieving_last():
    columns_init = ["iter", "score"]
    logger = logging.create_logger(
        name="retrieving_last",
        dir_name=TMP_LOGGER_DIR,
        columns=columns_init,
    )
    logger.info({"iter": 0, "score": .4})
    logger.info({"iter": 1, "score": .1})
    logger.info({"iter": 2, "score": .8})
    logger.info({"iter": 3, "score": 1.5})
    result = logger.query(f"""
SELECT score
FROM {logger.name}
ORDER BY iter DESC
LIMIT 1
""")

    assert len(result) == 1
    assert result[0][0] == 1.5

    teardown_logger(logger)


def test_aggregation():
    columns_init = ["iter", "score"]
    logger = logging.create_logger(
        name="test_aggregation",
        dir_name=TMP_LOGGER_DIR,
        columns=columns_init,
    )
    logger.info({"iter": 0, "score": .4})
    logger.info({"iter": 1, "score": .1})
    logger.info({"iter": 2, "score": .8})
    logger.info({"iter": 3, "score": 1.5})
    result = logger.query(f"""
SELECT SUM(score)
FROM {logger.name}
""")

    assert len(result) == 1
    assert result[0][0] == 2.8

    teardown_logger(logger)
