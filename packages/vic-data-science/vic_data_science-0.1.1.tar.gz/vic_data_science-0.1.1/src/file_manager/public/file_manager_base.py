"""
FileManager Module

This module contains the FileManager class, which provides a convenient way
to manage and manipulate different types of data sources and convert them to
Pandas DataFrames.
"""
from abc import ABC, abstractmethod


class file_manager_base(ABC):
    """
    FileManager Class

    The FileManager class is responsible for managing different data source and 
    converting them into Pandas DataFrames.
    """
    @abstractmethod
    def convert_to_dataframe(self, **kwargs):
        """
        Convert Data Source to Pandas DataFrame

        This method converts the specified data source to a Pandas DataFrame.

        Args: **kwargs: Additional keyword arguments for customizing the
        conversion process. The available keyword arguments depend on the
        data source type.

        Returns:
            pandas.DataFrame: The data from the data source as a DataFrame.
        
        Example:
            file_manager = FileManager('csv', 'data.csv')
            df = file_manager.convert_to_dataframe()
        """
        pass

    @abstractmethod
    def convert_to_file(self, **kwargs) -> None:
        """
        Convert Pandas DataFrame to Data Source

        This method converts the specified Pandas DataFrame to a data source.

        Args: **kwargs: Additional keyword arguments for customizing the
        conversion process. The available keyword arguments depend on the
        data source type.

        Example:
            file_manager = FileManager('csv', 'data.csv')
            df = file_manager.convert_to_dataframe()
        """
        pass