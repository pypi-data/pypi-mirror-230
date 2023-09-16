from ..private_repo._file_manager_sqlite import FileManagerSQLite


class FileManagerFactory:
    @staticmethod
    def create_file_manager(data_file_path: str):
        if ".db" in data_file_path:
            return FileManagerSQLite(data_file_path)
        raise ValueError(
            f"{data_file_path} with extension {data_file_path.split('.')[1]}")
