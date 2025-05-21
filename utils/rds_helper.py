import logging
import boto3
from .connection import Connection
from .config import Config


class RDSHelper:
    def __init__(self, dno_name=None, config=None):
        self.config = config or Config(dno_name)
        self.connection = Connection.getInstance(config=self.config)

        if not self._is_connection_alive():
            raise Exception("DB Connectivity Issue")

        self.client = boto3.client('rds')

    def _is_connection_alive(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1;")
            cursor.fetchall()
            logging.info("DB connection is alive")
            return True
        except Exception as ex:
            logging.error(f"DB connection failed: {ex}")
            return False

    def _convert_result_to_dict(self, rows, description):
        column_names = [col[0] for col in description]
        return [dict(zip(column_names, row)) for row in rows]

    def execute_query(self, sql, params=None):
        params = params or {}
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            result = self._convert_result_to_dict(rows, cursor.description)
            cursor.close()
            return result
        except Exception as ex:
            logging.error(f"Query execution failed: {ex}")
            raise

    def execute_command(self, sql, params=None):
        params = params or {}
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected
        except Exception as ex:
            self.connection.rollback()
            logging.error(f"Command execution failed: {ex}")
            raise

    def execute_command_returning_id(self, sql, params=None):
        params = params or {}
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            new_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            return new_id
        except Exception as ex:
            self.connection.rollback()
            logging.error(f"Insert command failed: {ex}")
            raise
