from abc import ABC
from typing import List

import pandas as pd
import sqlite3
import sys
import traceback

from ..public.file_manager_base import file_manager_base
from src.database_manager.databasemanager import DatabaseManager


class FileManagerSQLite(file_manager_base):

    def __init__(self, db_file: str):
        self.db_file = db_file

    def convert_to_dataframe(self, **kwargs):
        # ToDo : Try-Catch the kwargs
        table_name: str = kwargs.get("table_name", "")
        query: str = f"SELECT * FROM {table_name}"
        conn = sqlite3.connect(self.db_file)

        try:
            return pd.read_sql(query, conn)

        # ToDo : Incorporate exception
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            conn.close()

    def convert_to_file(self, data: pd, **kwargs) -> None:
        table_name: str = kwargs.get("table_name", "")
        db_manager = DatabaseManager(
            file_path_db=self.db_file
        )
        db_manager.connect()
        data.to_sql('my_table', db_manager.connection, if_exists='replace',
                    index=False)
        db_manager.disconnect()

    def convert_to_file_old(self, **kwargs):
        pandas_dataframe = kwargs.get("pandas_dataframe", None)
        sql_script_to_execute: str = kwargs.get("sql_script_to_execute", [])
        sql_file_name_path: str = kwargs.get("sql_file_name_path", "")
        schema_attributes = kwargs.get("schema_attributes", "")
        table_name: str = kwargs.get("table_name", "")
        column_names: str = kwargs.get("column_names", "")
        records: str = kwargs.get("records", "")

        db_manager = DatabaseManager(
            file_path_db=self.db_file,
            file_path_sql=sql_file_name_path
        )
        db_manager.connect()

        if 'create_schema' in sql_script_to_execute:
            db_manager.execute_sql_script(
                script_name="create_schema.sql",
                schema_attributes=schema_attributes,
                table_name=table_name)

        if 'insert_into_table' in sql_script_to_execute:
            db_manager.execute_sql_script(
                script_name="insert_into_table.sql",
                table_name=table_name,
                column_names=column_names,
                records=records)

        db_manager.disconnect()

        # ToDo : Create Exception if db file is not provided
        # ToDo : Create Exception if sql file is not provided
