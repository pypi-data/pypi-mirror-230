import os
import logging
from airtable import Airtable

from utilspkg import utils_init

if __name__ == '__main__':
    utils_init.load_env_variables_from_yaml('/Users/croft/VScode/ptagit/env_vars.yaml')

logger = utils_init.setup_logger(__name__)
# logger = logging.getLogger(__name__)

class DBConnect:
    """Class to interact with Airtable API"""

    def __init__(self, base_id=None, api_key=None, table_name=""):
        # Load environment variables if not provided
        self.base_id = base_id if base_id else os.environ['AIRTABLE_BASE_KEY']
        self.api_key = api_key if api_key else os.environ['AIRTABLE_API_KEY']
        self.table_name = table_name

    def get_table_object(self, table_name=""):
        """Return the Airtable object for given table_name"""
        
        # If we received the tablename argument, use that, else use the self variable
        table_name = table_name if table_name else self.table_name

        if not table_name:
            raise ValueError("table_name must be provided")

        try:
            return Airtable(base_id=self.base_id, table_name=table_name, api_key=self.api_key)
        except Exception as e:
            print(f"Error in getting table object: {e}")
            raise

    def helper_table_name_or_object (self, table_name_or_object):
        '''Class helper function to test if the user sent a table name or an object. Returns a table object '''
        if isinstance(table_name_or_object, str): #we got a table name 'string'
            table_object = self.get_table_object(table_name_or_object)
            # table_object.get_all(

        elif table_name_or_object is not None: # we think we got a table object
            table_object = table_name_or_object
        
        else:
            table_object = None
            raise ValueError("table_name_or_object must be provided")
        
        return table_object

    def get_records (self, table_name_or_object, **kwargs):
        """Returns table records. Optional kwargs:
         - formula=str,
         - sort=[], 
         - max_records=#, 
         - fields = ['Field1', 'Field2', 'Field3']
         """
        kwargs = {key: value for key, value in kwargs.items() if value is not None}

        table_object = self.helper_table_name_or_object(table_name_or_object)

        return table_object.get_all (**kwargs)
    
    
    def get_record (self, table_name_or_object, record_id):
        """
        The get_record function retrieves a record from the Airtable API.
        :param table_name_or_object: Determine whether the table name or object is being passed in
        :param record_id: Specify which record to retrieve
        :return: A record from a table
        """

        table_object = self.helper_table_name_or_object(table_name_or_object)

        return table_object.get(record_id)


    def search_table(self, table_name_or_object, field_name, search_text):
        """Search for records in a table with a specific field matching the search_text"""
        table_object = self.helper_table_name_or_object(table_name_or_object)

        return table_object.search(field_name, search_text)

    def update_record(self, table_name_or_object, record_id, record_dict):
        '''Runs table.update(recordid, recordfields) on table_name_or_object'''
        table_object = self.helper_table_name_or_object(table_name_or_object)
        
        return table_object.update(record_id=record_id, fields=record_dict)


    def insert_record(self, table_name_or_object, record_dict):
        '''Runs table.insert(record_dict) on table_name_or_object'''
        table_object = self.helper_table_name_or_object(table_name_or_object)

        try:
            return table_object.insert(fields=record_dict)
        except Exception as e:
            print(f"Error in inserting record: {e}")
            raise
