import pandas as pd
import numpy as np
import json
import os
import sqlalchemy
import time
import uuid
import pkg_resources
from sqlalchemy import text, inspect
from contextlib import contextmanager
from psycopg2 import sql
from io import StringIO
from typing import Type
from collections.abc import Iterable

from .frog_log import get_logger

# TODO: 
# How to support feedback in CF UI?
# Will need extensions for custom tables in a model
# Profile parallel write for xlsx
# Add batching to standard table writing

# Define chunk size (number of rows to write per chunk)
UPSERT_CHUNK_SIZE = 1000000

MASTER_LIST_PATH = 'anura/table_masterlists/anuraMasterTableList.json'
TABLES_DIR = 'anura/table_definitions'

class ValidationError(Exception):
    """Exception raised for validation errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class FrogModel:

    anura_tables = []
    anura_keys = {}
    anura_cols = {}

    @classmethod
    def _read_anura(cls: Type['FrogModel']):
        FrogModel._read_tables()
        FrogModel._read_pk_columns()

    
    @classmethod
    def _read_tables(cls: Type['FrogModel']):

        file_path = pkg_resources.resource_filename(__name__, MASTER_LIST_PATH)
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            FrogModel.anura_tables = [item["Table"].lower() for item in data]


    @classmethod 
    def _read_pk_columns(cls: Type['FrogModel']):

        file_path = pkg_resources.resource_filename(__name__, TABLES_DIR)

        # Iterate over each file in the directory
        for filename in os.listdir(file_path):

            filepath = os.path.join(file_path, filename)

            with open(filepath, 'r') as f:
                data = json.load(f)
                
            table_name = data.get("TableName").lower()
            
            # Extract the column names where "PK" is "Yes"
            all_columns = [field["Column Name"].lower() for field in data.get("fields", [])]
            pk_columns = [field["Column Name"].lower() for field in data.get("fields", []) if field.get("PK") == "Yes"]
            
            FrogModel.anura_cols[table_name] = all_columns
            FrogModel.anura_keys[table_name] = pk_columns


    def __init__(self, connection_string: str = None, engine: sqlalchemy.engine.Engine = None) -> None:

        self.engine = None
        self.connection = None
        self.transactions = [] 
        self.log = get_logger()

        # One time read in of Anura data
        if not FrogModel.anura_tables:
            self.log.info("Reading Anura schema")
            FrogModel._read_anura()

        # Initialise connection
        if engine is not None:
            self.engine = engine
        elif connection_string is not None:
            self.engine = sqlalchemy.create_engine(connection_string, connect_args={'connect_timeout': 15}) 

    
    def __enter__(self):
        self.start_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exceptions occurred, so commit the transaction
            self.commit_transaction()
        else:
            # An exception occurred, so roll back the transaction
            self.rollback_transaction()

    def __generate_index_sql(self, index_name, table_name, key_column_list, placeholder_value):
        
        coalesced_columns = ', '.join([f'COALESCE({column}, \'{placeholder_value}\')' for column in key_column_list])

        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({coalesced_columns});"
        
        return sql

    # Note: The following are for user managed transactions (do not use for library internal transactions)
    def start_transaction(self):
        if self.connection is None:
            self.connection = self.engine.connect()
        
        if self.transactions:
            self.transactions.append(self.connection.begin_nested())
        else:
            self.transactions.append(self.connection.begin())

    def commit_transaction(self):
        if self.transactions:
            transaction = self.transactions.pop()
            transaction.commit()

            if not self.transactions:
                self.connection.close()
                self.connection = None


    def rollback_transaction(self):
        if self.transactions:
            transaction = self.transactions.pop()
            transaction.rollback()

            if not self.transactions:
                self.connection.close()
                self.connection = None

    @contextmanager
    def begin(self):

        connection = None
        try:
            # Decide the context based on the transaction state
            if self.transactions: # If user has opened a transaction, then nest one
                connection = self.transactions[-1].connection
                transaction = connection.begin_nested()
            else: # else start a new one
                connection = self.engine.connect()
                transaction = connection.begin()
            
            yield connection  # yield the connection, not the transaction

            transaction.commit()  # commit the transaction if everything goes well

        except Exception:
            transaction.rollback()
            raise
        finally:
            # If the connection was created in this method, close it.
            if not self.transactions:
                connection.close()

    # Dump data to a model table
    def write_table(self, table_name: str, data: pd.DataFrame | Iterable):
        """
        This pushes data into a model table from a data frame or iterable object

        Parameters:
        table_name (str): The target table
        data: The data to be written

        Returns:
        None
        """

        table_name = table_name.lower().strip()

        self.log.info("Writing table: " + table_name)

        if isinstance(data, pd.DataFrame) == False:
            data = pd.DataFrame(data)

        data.columns = data.columns.str.lower().map(str.strip)

        # Initial implementation - pull everything into a df and dump with to_sql
        with self.begin() as connection:
            data.to_sql(table_name, con=connection, if_exists="append", index=False)

        # Note: tried a couple of ways to dump the generator rows directly, but didn't
        # give significant performance over dataframe (though may be better for memory)
        # Decided to leave as is for now 

    # Read a model table to dataframe
    def read_table(self, table_name: str, id_col : bool= False):
        
        table_name = table_name.lower().strip()

        with self.begin() as connection:
            result = pd.read_sql(table_name, con = connection)
            if not id_col:
                result.drop(columns=["id"], inplace=True)
            return result
        
    # Clear a model table
    def clear_table(self, table_name : str):

        table_name = table_name.lower().strip()

        # delete any existing data data from the table
        self.exec_sql("delete from " + table_name)

        return True

    # Read from model using raw sql query
    def read_sql(self, query: str):

        with self.begin() as connection:
            return pd.read_sql_query(query, connection)

    # Execute raw sql on model
    def exec_sql(self, query: str | sql.Composed):

        with self.begin() as connection:
            connection.execute(text(query))

    # Upsert from a csv file to a model table
    def upsert_csv(self, table_name: str, filename: str):

        for chunk in pd.read_csv(filename, chunksize=UPSERT_CHUNK_SIZE, dtype=str, skipinitialspace=True):

            chunk.replace("", np.nan, inplace=True)
            self.upsert(table_name, chunk)

    # Upsert from an xls file to a model table
    def upsert_excel(self, filename: str):

        # TODO: If an issue could consider another way to load/stream from xlsx maybe?

        xls = pd.ExcelFile(filename)
        file_name_without_extension = os.path.basename(filename).replace('.xlsx','').replace('.xls','')
        # For each sheet in the file
        for sheet_name in xls.sheet_names:
            table_to_upload = file_name_without_extension if sheet_name[:5].lower() == "sheet" else sheet_name
            # read the entire sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)

            df.columns = df.columns.str.lower().map(str.strip)

            for i in range(0, len(df), UPSERT_CHUNK_SIZE):
                chunk = df[i:i+UPSERT_CHUNK_SIZE]
                chunk.replace("", np.nan, inplace=True)
                self.upsert(table_to_upload, chunk)


    def __get_table_columns(self, table_name: str):
        
        # Create an Inspector object
        inspector = inspect(self.engine)

        # Get the column names for a specific table
        column_names = inspector.get_columns(table_name)
        
        column_names = [column['name'] for column in column_names]

        return [name.lower().strip() for name in column_names]


    # Upsert from a dataframe
    def upsert(self, table_name: str, data: pd.DataFrame):

        table_name = table_name.strip().lower()

        data.columns = data.columns.str.lower().map(str.strip)

        if table_name not in FrogModel.anura_tables:
            #Skip it
            self.log.warning(f"""Worksheet name not recognised as Anura table (skipping): {table_name}""")
            return

        self.log.info(f"""Importing worksheet to table: {table_name}""")
        self.log.info(f"""Source data has {len(data)} rows""")

        # Behavior rules:
        # Key columns - get used to match (Note: possible future requirement, some custom columns may also be key columns)
        # Other Anura columns - get updated
        # Other Custom columns - get updated
        # Other columns (neither Anura or Custom) - get ignored

        all_column_names = self.__get_table_columns(table_name)
        if "id" in all_column_names:
            all_column_names.remove("id")

        # 1) Anura key cols - defined in Anura
        # 2) Custom key cols - TBD CF Meta
        # 3) Update cols - The rest

        anura_key_columns = FrogModel.anura_keys[table_name]
        custom_key_columns = [] 
        # This will later be populated from custom columns meta tables
        if "notes" in all_column_names:
            custom_key_columns.append("notes")
        combined_key_columns = anura_key_columns + custom_key_columns
        update_columns = [col for col in all_column_names if col not in combined_key_columns]


        # Skipping unrecognised rows (Do not trust column names from user data)
        cols_to_drop = [col for col in data.columns if col not in all_column_names]


        for col in cols_to_drop:
            self.log.info(f"""Skipping unknown column: {col}""")
        data = data.drop(cols_to_drop, axis=1)
         

        # Want to either make a transaction, or a nested transaction depending on the presence or absense
        # of a user transaction (if one exists then nest another, else create a root)
        with self.begin() as connection:

            # Create temporary table
            temp_table_name = "temp_table_" + str(uuid.uuid4()).replace('-', '')
            self.log.info(f"""Moving data to temporary table: {temp_table_name}""") 

            # Note: this will also clone custom columns
            create_temp_table_sql = f"""
                CREATE TEMPORARY TABLE {temp_table_name} AS
                SELECT *
                FROM {table_name}
                WITH NO DATA;
                """
            
            connection.execute(text(create_temp_table_sql))

            # Copy data from df to temporary table
            copy_sql = sql.SQL("COPY {table} ({fields}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)").format(
                table=sql.Identifier(temp_table_name),
                fields=sql.SQL(', ').join(map(sql.Identifier, data.columns))
            )

            # For key columns, replace Null with placeholder
            # For matching on key columns only, will not be written to final table!
            placeholder_value = ''  # replace with a value that does not appear in your data
            for column in combined_key_columns:
                data[column].fillna(placeholder_value, inplace=True)

            cursor = connection.connection.cursor()

            start_time = time.time()
            cursor.copy_expert(copy_sql, StringIO(data.to_csv(index=False)))
            end_time = time.time()
            self.log.info(f"Copy data to temporary table took {end_time - start_time} seconds")
            del data

            # Generate an index to speed up the update/insert queries 
            # Note: This is per 'chunk' rather than per file
            # TODO: Need more analysis on performance, likely revisit to create index once
            upsert_index_name = "cf_upsert_index_" + str(uuid.uuid4()).replace('-', '')
            index_sql = self.__generate_index_sql(upsert_index_name, table_name, combined_key_columns, placeholder_value)

            start_time = time.time()
            cursor.execute(index_sql)
            end_time = time.time()
            self.log.info(f"Index creation took {end_time - start_time} seconds")
            
            # Now upsert from temporary table to final table

            # Note: Looked at ON CONFLICT for upsert here, but seems not possible without defining constraints on target table
            # so doing insert and update separately

            all_columns_list = ", ".join([f'"{col_name}"' for col_name in all_column_names])

            if combined_key_columns:

                update_column_list = ", ".join([f'"{col_name}" = "{temp_table_name}"."{col_name}"' for col_name in update_columns])
                key_condition = " AND ".join([f'COALESCE("{table_name}"."{key_col}", \'{placeholder_value}\') = COALESCE("{temp_table_name}"."{key_col}", \'{placeholder_value}\')' for key_col in combined_key_columns])

                update_query = f"""
                    UPDATE {table_name}
                    SET {update_column_list}
                    FROM {temp_table_name}
                    WHERE {key_condition};
                """

                start_time = time.time()
                cursor.execute(update_query)
                updated_rows = cursor.rowcount
                end_time = time.time()
                self.log.info(f"Update query took {end_time - start_time} seconds")


                temp_columns_list = ", ".join([f'"{temp_table_name}"."{col_name}"' for col_name in all_column_names])
                null_conditions = [f"{table_name}.{col} IS NULL" for col in combined_key_columns]
                null_conditions_clause = " AND ".join(null_conditions)

                insert_query = f"""
                    INSERT INTO {table_name} ({all_columns_list})
                    SELECT {temp_columns_list}
                    FROM {temp_table_name}
                    LEFT JOIN {table_name}
                    ON {key_condition}
                    WHERE {null_conditions_clause}
                """

                start_time = time.time()
                cursor.execute(insert_query)
                inserted_rows = cursor.rowcount 
                end_time = time.time()
                self.log.info(f"Insert query took {end_time - start_time} seconds")

                # Finally remove the index created for upsert
                # TODO: Finally block?
                cursor.execute(f'DROP INDEX IF EXISTS {upsert_index_name};')

            # If no key columns, then just insert
            else:
                insert_query = f"""
                    INSERT INTO {table_name} ({all_columns_list})
                    SELECT {all_columns_list}
                    FROM {temp_table_name}
                """
                
                updated_rows = 0
                self.log.info(f"""Running insert query.""")
                cursor.execute(insert_query)
                inserted_rows = cursor.rowcount 

        #TODO: Could return this?
        self.log.info("Updated rows  = {}".format(updated_rows))
        self.log.info("Inserted rows = {}".format(inserted_rows))