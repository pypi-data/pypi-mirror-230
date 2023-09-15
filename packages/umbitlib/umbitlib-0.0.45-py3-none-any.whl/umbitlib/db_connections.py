#%%
# Imports
import keyring as kr
import pandas as pd
import time
from urllib import parse

import sqlalchemy as sa
from sqlalchemy.engine import create_engine

from warnings import filterwarnings
filterwarnings("ignore")

from umbitlib.helpers import convert_seconds
from umbitlib.helpers import generate_sqlalchemy_dtypes

#%%
# Security
class SecurityHandler:
    """
    A class for handling security operations for various services.

    This class provides methods for initializing security instances and accessing service credentials.

    Args:
        service_name (str): The desired service name for security operations.
        NOTE: Valid service names: {'oracle', 'oracle_serv_acc', 'postgres_dev', 'postgres_prod', 'postgres_serv_acc'}

    Raises:
        ValueError: If the provided service_name is not one of the valid options.

    Example:
        orc = SecurityHandler('oracle')
    """

    _VALID_SERVICE_NAMES = {'oracle', 'oracle_serv_acc', 'postgres_dev', 'postgres_prod', 'postgres_serv_acc'}

    def __init__(self, service_name):
        """
        Initializes a security instance

        Args:
        service_name (str): The desired service_name for security operations.

        Raises:
        ValueError: If the provided service_name is not one of the valid options.

        Example:
        orc = SecurityHandler('oracle')
        """

        self._service_name = service_name.lower()

        if self._service_name not in self._VALID_SERVICE_NAMES:
            raise ValueError(f"service_name must be one of {self._VALID_SERVICE_NAMES}")

        self._security_obj = kr.get_credential(service_name=self._service_name, username=None)
        self.username = self._security_obj.username
        self._password = parse.quote_plus(self._security_obj.password)

    # Use of the @property decorator with no accompanying setter method ensures that the service_name cannot be set 
    # to another value after initialization. (Unless the user calls _service_name which is technically private)
    @property
    def service_name(self):
        """
        str: The selected service_name for security operations.
        """
        return self._service_name
    

# Engine Handler
class DatabaseEngine(SecurityHandler):
    """
    A class for managing database connections with various engines.

    This class inherits from SecurityHandler and provides methods to create database connections
    for different database engines, such as Oracle and PostgreSQL.

    Args:
        service_name (str): The desired service name for security operations, inherited from SecurityHandler.

    Example:
        engine = DatabaseEngine('oracle')
    """

    def __init__(self, service_name):
        """
        Initializes a database engine instance and establishes a connection to the specified database.

        Args:
            service_name (str): The desired service name for security operations, inherited from SecurityHandler.

        Example:
            engine = DatabaseEngine('oracle')
        """
        super().__init__(service_name)

        try:
            import sys
            sys.path.append("\\\\ad.utah.edu\\uuhc\\umb2\\shared\\Analytics Team\\Security")
            import db_conn_vars

        except ModuleNotFoundError as e:
            print(f"Security file not found: {e}")
            pass

        if self.service_name in ['oracle', 'oracle_serv_acc']:
            self._dsn = db_conn_vars.ODB_NAME
            self.engine = sa.create_engine(f"oracle+cx_oracle://{self.username}:{self._password}@{self._dsn}", echo=False)  # Set echo=True for debugging
        elif self.service_name in ['postgres_dev', 'postgres_prod', 'postgres_serv_acc']:
            if self.service_name == 'postgres_dev':
                self._db = db_conn_vars.PG_DEV_DB
                self._host = db_conn_vars.PG_DEV_HOST
                self._port = db_conn_vars.PG_DEV_PORT
            elif self.service_name == 'postgres_prod':
                self._db = db_conn_vars.PG_PROD_DB
                self._host = db_conn_vars.PG_PROD_HOST
                self._port = db_conn_vars.PG_PROD_PORT

            self.engine = create_engine(f"postgresql://{self.username}:{self._password}@{self._host}:{self._port}/{self._db}")


# SQL Handler
class SqlHandler(DatabaseEngine):
    """
    A class for executing SQL statements against databases.

    This class inherits from DatabaseEngine and provides methods for executing SQL queries on the database
    and uploading DataFrames to the database tables making a usable connection and other standard SQL functions.

    Args:
        service_name (str): The desired service name for security operations, inherited from DatabaseEngine.

    Example:
        sql_handler = SqlHandler('oracle')
    """

    def __init__(self, service_name):
        """
        Initializes an SQL handler instance.

        Args:
            service_name (str): The desired service name for security operations, inherited from DatabaseEngine.

        Example:
            sql_handler = SqlHandler('oracle')
        """
        super().__init__(service_name)


    def connect(self, conn_success_msg: bool = True):
        """
        Creates a connection to a database.  Requires that the programmer closes the connection in a separate statment.

        Args:
            conn_success_msg (bool): Determines if connection successful message will print out or not. Default = True

        Returns:
            A connection to the specified database
        
        Example:
            sql_handler = SqlHandler('oracle')

            sql_conn = sql_handler.connect()

                //your code here//

            sql_conn.close()
        """
        try:
            sql_connection = self.engine.connect()
            if conn_success_msg:
                print(f"Connection to {self.service_name} for user {self.username} via Keyring: Successful. Use of this function requires manual closing of this connection upon end of use.")
            return sql_connection
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None


    def query(self, sql_query, conn_success_msg: bool = True, sql_success_msg: bool = True):
        """
        Execute a SQL query on the database and return the result as a DataFrame.

        Args:
            sql_query (str): The SQL query to execute.
            conn_success_msg (bool): Turns on or off the output of the connection success message (default is True)
            query_success_msg (bool): Turns on or off the output of the query success message and runtime (default is True)

        Returns:
            pandas.DataFrame: A DataFrame containing the query result.

        Example:
            sql_handler = SqlHandler('oracle')

            df = sql_handler.query('SELECT * FROM your_table')
        """
        try:
            with self.engine.connect() as connection:
                if conn_success_msg:
                    print(f"Connection to {self.service_name} for user {self.username} via Keyring: Successful")
                sql_text = sa.text(sql_query)
                tic = time.perf_counter()
                result_df = pd.read_sql(sql_text, con=connection)
                toc = time.perf_counter() 

                if sql_success_msg:
                    try:
                        elapsed_time = toc - tic
                        days, hours, minutes, seconds = convert_seconds(elapsed_time)
                        print(f"Query executed without error in {days}d:{hours}h:{minutes}m:{round(seconds,2)}s.")
                    except:
                        print("Problem getting elapsed time")
                        pass
            
            return result_df
        except Exception as e:
            print(f"Error executing query against {self.service_name}: {e}.")
            return None
        
    
    def upload_df(self, dataframe, table_name, table_mgmt='truncate', index=False, dtype=None, conn_success_msg: bool = True, sql_success_msg: bool = True):
        """
        Upload a DataFrame to the database. By default, this function converts the dataframe column types to sqlalchmeny column types when uploading.
        A user can override this auto-conversion by passing their own dict of column typing where the key is the column_name and the value
        is the sqlalchemy_column_type.  

        Args:
            dataframe (pandas.DataFrame): The DataFrame to upload.
            table_name (str): The name of the table to upload the DataFrame to.
            if_exists (str, optional): How to behave if the table already exists. Defaults to 'truncate'. ('truncate', 'replace', 'append', 'fail')
            index (bool, optional): Whether to include the DataFrame index as a column. Defaults to False.
            dtype (dict, optional): Overrides the auto type detection with user-defined type mapping that is applied to the columns. Defaults to None.
            conn_success_msg (bool): Turns on or off the output of the connection success message (default is True)
            query_success_msg (bool): Turns on or off the output of the query success message and runtime (default is True)

        Example:
            sql_handler = SqlHandler('oracle')

            sql_handler.upload_df(your_dataframe, 'my_table')

            Example without auto_dtype:
                import sqlalchemy as sa

                my_dtypes = {'int_col': sa.types.INTEGER(),
                            'str_col': sa.types.VARCHAR(length=30),
                            'bool_col': sa.types.BOOLEAN(),
                            'dt': sa.types.DATE()}

                sql_handler.upload_df(your_dataframe, 'my_table' , dtype=my_dtypes)

        Notes:
            For full list of acceptable types see https://docs.sqlalchemy.org/en/20/core/type_basics.html#types-sqlstandard 
            under the SQL Standard and Multiple Vendor “UPPERCASE” Types section

            The automatic conversion is based on the dataframe's datatypes. Hence, if a date field is listed as an object datatype 
            in the dataframe the auto-conversion will set it as a VARCHAR.  To rectify this, please cast your dataframe columns to 
            the desired data types prior to using this function or override the auto-conversion using the dtype argument.  
            In the example given if the auto-conversion is overridden and a date (which is an object datatype in the df) is set to 
            a sqlalchemy date then it will upload as a date.
        """
        try:
            pg_dtype = generate_sqlalchemy_dtypes(dataframe)

            if dtype is not None:
                pg_dtype = dtype
            
            # Upload DataFrame
            with self.engine.begin() as connection:
                if conn_success_msg:
                    print(f"Connection to {self.service_name} for user {self.username} via Keyring: Successful")

                tic = time.perf_counter()
                if table_mgmt == 'truncate':
                    trunc_sql = sa.text(f'TRUNCATE TABLE {table_name}')
                    connection.execute(trunc_sql)
                    dataframe.to_sql(table_name, connection, if_exists='append', index=index, dtype=pg_dtype)
                else:
                    dataframe.to_sql(table_name, connection, if_exists=table_mgmt, index=index, dtype=pg_dtype)
                toc = time.perf_counter() 

                if sql_success_msg:
                    try:
                        elapsed_time = toc - tic
                        days, hours, minutes, seconds = convert_seconds(elapsed_time)
                        print(f"Sql executed without error in {days}d:{hours}h:{minutes}m:{round(seconds,2)}s.")
                    except:
                        print("Problem getting elapsed time")
                        pass
                
            print(f"DataFrame uploaded successfully to {self.service_name}.")
            
        except Exception as e:
            print(f"Error uploading DataFrame to {self.service_name}:", str(e))

    
    def drop_table(self, table_name, conn_success_msg: bool = True, sql_success_msg: bool = True):
        """
        Drop a table from the database.

        Args:
            table_name (str): The name of the table to drop.
            conn_success_msg (bool, optional): Whether to print connection success message.
                Defaults to True.
            sql_success_msg (bool, optional): Whether to print SQL execution success message.
                Defaults to True.

        Returns:
            None

        Raises:
            Exception: If there's an error executing the DROP TABLE statement.

        Example:
            sql_handler = SqlHandler('postgres_dev')
            
            sql_handler.drop_table('my_table')
        """

        try:    
            with self.engine.begin() as connection:
                if conn_success_msg:
                    print(f"Connection to {self.service_name} for user {self.username} via Keyring: Successful")

                drop_sql = sa.text(f"DROP TABLE IF EXISTS {table_name};")
                tic = time.perf_counter()    
                connection.execute(drop_sql)
                toc = time.perf_counter()

                if sql_success_msg:
                    try:
                        elapsed_time = toc - tic
                        days, hours, minutes, seconds = convert_seconds(elapsed_time)
                        print(f"Sql executed without error in {days}d:{hours}h:{minutes}m:{round(seconds,2)}s.")
                    except:
                        print("Problem getting elapsed time")
                        pass

            print(f"Table {table_name} dropped successfully from {self.service_name}.")
            
        except Exception as e:
            print(f"Error executing DROP TABLE from {self.service_name}:", str(e))
