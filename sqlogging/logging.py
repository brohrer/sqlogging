import os
import sqlite3

DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

def create_logger(
    name="log",
    dir_name="logs",
    level="info",
    columns=["ts", "data"],
):
    level_str = level.upper()
    if level_str == "DEBUG":
        level = DEBUG
    elif level_str == "INFO":
        level = INFO
    elif level_str == "WARNING":
        level = WARNING
    elif level_str == "ERROR":
        level = ERROR
    elif level_str == "CRITICAL":
        level = CRITICAL
    else:
        raise ValueError(
            "level must be one of 'debug', 'info', 'warning', 'error', or 'critical'")

    logger = Logger(name, dir_name, level=level, columns=columns, create=True)
    return logger


def open_logger(
    name="log",
    dir_name="logs",
):
    logger = Logger(name, dir_name, create=False)
    return logger


class Logger:
    def __init__(self, name, dir_name, level=None, columns=None, create=True):
        self.name = name
        self.dir_name = dir_name
        self.db_path = os.path.join(self.dir_name, self.name)

        if create:
            os.makedirs(self.dir_name, exist_ok=True)
            self.level = level

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        if create:
            create_table_sql = f"""
                CREATE TABLE {self.name} ({', '.join(columns)});
                """
            self.cursor.execute(create_table_sql)

        table_info = self.query(f"PRAGMA table_info({self.name});")
        self.columns = []
        self.col_indices = {}
        for i_col, row in enumerate(table_info):
            col_name = row[1]
            self.columns.append(col_name)
            self.col_indices[col_name] = i_col

    def get_columns(self):
        return self.columns

    def delete(self):
        """
        Delete both the table and the database that contained it.
        """
        delete_table_sql = f"DROP TABLE {self.name};"
        self.cursor.execute(delete_table_sql)
        self.connection.close()
        os.remove(self.db_path)

    def close(self):
        self.connection.close()

    def debug(self, data):
        if self.level <= DEBUG:
            self._write(data)

    def info(self, data):
        if self.level <= INFO:
            self._write(data)

    def warning(self, data):
        if self.level <= WARNING:
            self._write(data)

    def error(self, data):
        if self.level <= ERROR:
            self._write(data)

    def critical(self, data):
        if self.level <= CRITICAL:
            self._write(data)

    def _write(self, data):
        data_list = [None] * len(self.columns)

        for key, val in data.items():
            data_list[self.col_indices[key]] = val
        data_tuple = tuple(data_list)

        # Using question mark placeholders lets us lean on sqlite to
        # format our various types correctly. It also protects the
        # log table in case a nefarious lab mate tries to execute
        # a SQL injection attack.
        qmarks = ["?"] * len(self.columns)
        qmarks_commas = ", ".join(qmarks)
        insert_sql = (f"INSERT into {self.name} VALUES({qmarks_commas});")
        self.cursor.execute(insert_sql, data_tuple)
        self.connection.commit()

    def query(self, query_str):
        result = self.cursor.execute(query_str)
        return result.fetchall()
