import os
from typing import List

from dftools.exceptions import MissingMandatoryArgumentException, NoFileAtLocation

class ConnectionWrapper():
    """
        Connection Wrapper interface
        All connection wrappers should implement this interface
    """

    # Connection methods
    def get_current_catalog(self) -> str:
        """
        Returns the currently active catalog for this connection.
        
        Returns
        -----------
            catalog_name : str
                The catalog name
        """
        return NotImplementedError('The get_current_catalog method is not implemented')

    def get_current_namespace(self) -> str:
        """
        Returns the currently active namespace (also named schema) for this connection.
        
        Returns
        -----------
            namespace : str
                The namespace
        """
        return NotImplementedError('The get_current_namespace method is not implemented')
    
    def close_connection(self):
        """
        Closes the connection currently stored in this wrapper

        Returns
        -----------
            close_status : str
                The connection close status
        """
        return NotImplementedError('The close_connection method is not implemented')

    # Query and script execution methods

    def execute_script(self, file_path : str, delimiter : str = ';') -> list :
        """
        Executes a script on the connection wrapper provided.

        Parameters
        -----------
            file_path : str
                The file path of the script to execute
            delimiter : str
                The statements' delimiter (defaulted to ";")
        
        Returns
        -----------
            None
        """
        if file_path is None :
            raise MissingMandatoryArgumentException(method_name='Execute Script', object_type=type(self), argument_name='File Path')
        if not os.path.exists(file_path):
            raise NoFileAtLocation(file_path=file_path)
        with open(file_path, 'r') as file :
            file_data = file.read()
        queries = file_data.split(delimiter)
        return self.execute_queries(queries)
    
    def execute_query(self, query : str) -> list:
        """
        Executes a query on the connection contained in the wrapper.
        An error should be raised according to the specificities of each database

        Parameters
        -----------
            query : The query to execute
        
        Returns
        -----------
            result_set_list : The list of result set, or None if query encountered an error
        """
        return NotImplementedError('The execute_query method is not implemented')
    
    def execute_queries(self, query_list : List[str]) -> list:
        """
        Executes a list of queries on the snowflake connection contained in the wrapper.
        An error should be raised according to the specificities of each database

        Parameters
        -----------
            query_list : The list of queries to execute
        
        Returns
        -----------
            None
        """
        return NotImplementedError('The execute_queries method is not implemented')