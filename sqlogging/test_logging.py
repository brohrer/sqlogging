import os
import shutil
import sqlite3
import time
from sqlogging import logging


def teardown_logger(logger):
    logger.delete()
    shutil.rmtree(logger.dir_name)
    del logger


def test_logger_creation():
    logger_name = f"test_logger_{int(time.time())}"
    logger = logging.create_logger(name=logger_name)
    assert logger.name == logger_name

    teardown_logger(logger)


def test_logging_dir_creation():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
    )
    assert logger.dir_name == logger_dir_name
    assert logger.db_path == os.path.join(logger_dir_name, logger_name)
    assert os.path.isdir(logger_dir_name)

    teardown_logger(logger)


def test_levels():
    assert logging.DEBUG == 10
    assert logging.INFO == 20
    assert logging.WARNING == 30
    assert logging.ERROR == 40
    assert logging.CRITICAL == 50


def test_level_setting():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        level="debug",
        dir_name=logger_dir_name,
    )

    assert logger.level == 10

    teardown_logger(logger)


def test_level_validation():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    try:
        logger = logging.create_logger(
            name=logger_name,
            level="circuital",
            dir_name=logger_dir_name,
        )
        assert False
        teardown_logger(logger)
    except ValueError:
        assert True


def test_default_columns():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        level="debug",
        dir_name=logger_dir_name,
    )

    table_info = logger.query(f"PRAGMA table_info({logger_name});")
    columns = []
    for row in table_info:
        columns.append(row[1])

    assert len(columns) == 2
    assert "ts" in columns
    assert "data" in columns

    teardown_logger(logger)


def test_column_assignment():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    columns_init = ["time", "iteration", "d3_score", "ABC", "B02349"]
    logger = logging.create_logger(
        name=logger_name,
        level="debug",
        dir_name=logger_dir_name,
        columns=columns_init,
    )

    table_info = logger.query(f"PRAGMA table_info({logger_name});")
    columns = []
    for row in table_info:
        columns.append(row[1])

    assert len(columns) == 5
    for col in columns_init:
        assert col in columns

    teardown_logger(logger)


def test_log_delete():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
    )
    table_info = logger.query(f"PRAGMA table_info({logger_name});")
    assert len(table_info) == 2

    logger.delete()
    try:
        table_info = logger.query(f"PRAGMA table_info({logger_name});")
        assert False
    except sqlite3.ProgrammingError:
        assert True

    shutil.rmtree(logger.dir_name)
    del logger


def test_log_close():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
    )
    table_info = logger.query(f"PRAGMA table_info({logger_name});")
    assert len(table_info) == 2

    logger.close()
    try:
        table_info = logger.query(f"PRAGMA table_info({logger_name});")
        assert False
    except sqlite3.ProgrammingError:
        assert True

    shutil.rmtree(logger.dir_name)
    del logger


def test_log_reopen():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    columns_init = ["time", "iteration", "d3_score", "ABC", "B02349"]
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
        columns=columns_init,
    )
    table_info = logger.query(f"PRAGMA table_info({logger_name});")
    assert len(table_info) == 5

    logger.close()

    try:
        logger = logging.create_logger(
            name=logger_name,
            dir_name=logger_dir_name,
        )
        assert False
    except sqlite3.OperationalError:
        assert True

    logger = logging.open_logger(
        name=logger_name,
        dir_name=logger_dir_name,
    )
    table_info = logger.query(f"PRAGMA table_info({logger_name});")
    assert len(table_info) == 5

    teardown_logger(logger)


def test_writing_debug():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
    )
    logger.info({"ts": 23874.2234, "data": "flurpy"})
    result = logger.query(f"SELECT * FROM {logger_name};")
    assert len(result) == 1
    assert result[0][0] == 23874.2234
    assert result[0][1] == "flurpy"

    columns = logger.get_columns()
    assert columns[0] == "ts"
    assert columns[1] == "data"

    teardown_logger(logger)


def test_writing_below_severity():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
        level="warning",
    )
    logger.debug({"ts": 42, "data": "bing bang"})
    result = logger.query(f"SELECT * FROM {logger_name};")
    assert len(result) == 0

    teardown_logger(logger)


def test_writing_above_severity():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
        level="debug",
    )
    logger.critical({"ts": 100000000, "data": "mayhem!"})
    logger.error({"ts": -999, "data": "badness occurred"})
    result = logger.query(f"SELECT * FROM {logger.name};")
    assert len(result) == 2

    teardown_logger(logger)


def test_writing_partial_rows():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    columns_init = ["timestamp", "iteration", "d3_score"]
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
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
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
    )
    try:
        logger.critical({"iteration": 398})
        assert False
    except KeyError:
        assert True

    teardown_logger(logger)


def test_retrieving_last():
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    columns_init = ["iter", "score"]
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
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
    logger_name = f"test_logger_{int(time.time())}"
    logger_dir_name = f"test_logger_{int(time.time())}_dir"
    columns_init = ["iter", "score"]
    logger = logging.create_logger(
        name=logger_name,
        dir_name=logger_dir_name,
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
