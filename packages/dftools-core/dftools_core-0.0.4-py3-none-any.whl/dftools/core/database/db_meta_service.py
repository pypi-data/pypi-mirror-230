import json
from typing import List

from dftools.core.database.connection_wrapper import ConnectionWrapper
from dftools.core.structure import BaseStructureDecoder, Structure

class DatabaseMetadataService():
    """
        Database Metadata Service interface
        
        All database implementation should implement this interface
    """

    def __init__(self, connection_wrapper : ConnectionWrapper, decoder : BaseStructureDecoder) -> None:
        self.conn_wrap = connection_wrapper
        self.decoder = decoder
    
    def get_structure_from_database(self, namespace : str, table_name : str) -> list:
        """
            Get a structure from the database using the 

            Parameters
            -----------
                namespace : str
                    The namespace name (also named schema)
                table_name : str
                    The table name

            Returns
            -----------
                data_structure_dict : a dictionnary of the data structure dictionnary
            
        """
        return NotImplementedError('The get_structure_from_database method is not implemented')
    
    def decode_specific_structure_result_set(self, result_set : list) -> None:
        structure_list = []
        for row in result_set:
            cur_data = row[0]
            structure_meta = json.loads(cur_data)
            std_structure_meta = self.decoder.decode_json(structure_meta)[1]
            structure_list.append(std_structure_meta)
        return structure_list

    def get_standard_structure_from_database(self, namespace : str, table_name : str) -> List[Structure]:
        """
            Get a standard structure from the database

            Parameters
            -----------
                namespace : str
                    The namespace name (also named schema)
                table_name : str
                    The table name

            Returns
            -----------
                data_structure_list : List[Structure]
                    A list of structures
        """
        current_namespace = namespace if namespace is not None else self.conn_wrap.get_current_namespace()
        return self.decode_specific_structure_result_set([self.get_structure_from_database(current_namespace, table_name)])