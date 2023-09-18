import sqlite3


class DatabaseManager:
    def __init__(self, file_path_db: str, file_path_sql: str=None):
        self.cursor = None
        self.connection = None
        self.file_path_db: str = file_path_db
        self.file_path_sql: str = file_path_sql

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.file_path_db)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def read_script(self, script_name: str) -> str:
        sql_full_path: str = f"{self.file_path_sql}/{script_name}"
        try:
            with open(sql_full_path, "r") as sql_file:
                return sql_file.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"SQL file '{sql_full_path}' not found.")

    def execute_sql_script(self, **kwargs):
        script_name: str = kwargs.get("script_name", "")
        table_name: str = kwargs.get("table_name", "")
        schema_attributes: str = kwargs.get("schema_attributes", "")
        column_names: str = kwargs.get("column_names", "")
        records: str = kwargs.get("records", [])

        # Read the SQL script from the file
        sql_script: str = self.read_script(script_name=script_name)

        # Replace placeholders with actual values
        sql_script = self._query_builder(sql_script,
                                         placeholder=":table_name:",
                                         sql_param=table_name)
        sql_script = self._query_builder(sql_script,
                                         placeholder=":schema_attributes:",
                                         sql_param=schema_attributes)
        sql_script = self._query_builder(sql_script,
                                         placeholder=":column_names:",
                                         sql_param=column_names)

        try:
            if len(records) > 0:
                for record in records:
                    sql_script_tempt = self \
                        ._query_builder(sql_script,
                                        placeholder=":records:",
                                        sql_param=str(record))
                    self.cursor.execute(sql_script_tempt)
            else:
                self.cursor.execute(sql_script)
            self.connection.commit()
        except Exception as e:
            print(f"Error executing script {sql_script}: {e}")

    def _query_builder(self, sql_script: str, placeholder: str,
                       sql_param: str) -> str:
        if sql_param:
            return sql_script.replace(f"{placeholder}", sql_param)
        return sql_script
