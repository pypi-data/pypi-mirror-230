import psycopg2
import pandas as pd
import time
import cx_Oracle
import os
import os.path
from umbitlib.constants import * # !!! Change this to 'import src.umbitlib.constants' for testing and back to 'from umbitlib.constants import *' for production upload
from umbitlib.dates import * # !!! Change this to 'import src.umbitlib.dates' for testing and back to 'from umbitlib.dates import TRGTMON_YYYYMMDD' for production upload
import warnings


####################################################################################
## ORACLE CONNECTION FUNCTIONS
####################################################################################

def excel_credentials():   
    """
    Summary:
        Function to retrieve UofU credentials saved in specified Excel doc in G drive.

    Returns:
        username and password from Excel doc in tuple.

    Example:        
        username, password = excel_credentials()
    """    
    try:  
        data_source_file_oracle = r"G:\Data Sources\UIDPWD.xlsx"
        wb_credentials_oracle = load_workbook(data_source_file_oracle)
        sheet_oracle = wb_credentials_oracle['Sheet1']
        username = sheet_oracle['A2'].value
        password = sheet_oracle['B2'].value
        return username, password
    except:
        raise TypeError('Excel workbook with credentials not found.')
    
def oracle_connection(username: str=None, password: str=None)->cx_Oracle.Connection:
    """
    Summary:
        Function to initialize connection to Oracle. Uses stored Excel credentials by default.\n
        If no Excel credentials are found, attempts to access environment variables stored as 'ORACLE_USERNAME' and 'ORACLE_PASSWORD'. \n
        User may override default checks by manually entering username and password via key entry or passed environment variables.

    Returns:
        cx_Oracle.Connection: As "connection_oracle"

    Note:
        Setting a variable equal to function grants all cx_Oracle functions (i.e. .cursor())

    Example:        
        Set connection variable: conn = init_oracle_conn() 
        Set cursor variable: cursor = conn.cursor()
        Save query results to dataframe: df = pd.read_sql_query(sqlQueryString, conn)
    """    

    if not username and not password:
        try:
            username, password = excel_credentials()
        except:
            try:
                username = os.environ['ORACLE_USERNAME']
                password = os.environ['ORACLE_PASSWORD']     
            except:
                try:
                    username = ORACLE_USER
                    password = ORACLE_PASS
                except:
                    raise TypeError('Excel credentials workbook and environment variables failed. Please try manually entering credentials.')  

    if password and username:
        try: 
            oracle_connection = cx_Oracle.connect(
            username, password, "DWRAC_UMB_UUMG")
            print('Connection successful.')
            return oracle_connection  
        except:
            raise TypeError('Connection failed. Supplied credentials disallowed.')
    else:
        raise TypeError('Must supply both username AND password.')

def oracle_query(sql):
    """
    Summary:
        Sends a given SQL query string to Oracle and returns results as a dataframe object
        Function will also print out query duration time in seconds
        
    Requirements:
        The machine this is run on must have oracle drivers set up
        User must have EDW access and credentials

    Returns:
        pandas.dataframe

    Example:        
        Save results to dataframe: df = oracle_query(' SELECT * FROM CLARITY_REPORT.ZC_STATE ')
    """ 
    tic = time.perf_counter()
    connection = oracle_connection()                                
    df = pd.read_sql_query(sql, connection, parse_dates='post_period')
    connection.close()
    toc = time.perf_counter() 
    print(f"Query finished in {toc - tic:0.4f} seconds")
    return df


####################################################################################
## POSTGRES CONNECTION FUNCTIONS
####################################################################################

def postgres_connection(username:str=None, password:str=None, host:str=None, port:str=None, database:str=None, devMode: bool=True)->psycopg2.extensions.connection:
    """
    Summary:
        Function to initialize connection to Postgres.
        Uses credentials specified in the inputs or you can leave these blank and toggle between devMode True or false
    
    Args:
        username (str, optional): postgres database username
        password (str, optional): postgres database password
        host (str, optional): postgres database host machine IP Address
        port (str, optional): postgres host machine database port number (usually 5432)
        database (str, optional): postgres database/schema Name
        devMode (boolean, optional): Defaults to True, if False Production system environment variables are used instead of Dev variables
   
    Requirements:
        System environment variables need to be set up for the following:\n
            PG_DEV_USER (username)\n
            PG_DEV_PASS (password)\n
            PG_DEV_HOST (Host IP address)\n
            PG_DEV_PORT (IP port)\n
            PG_DEV_DB (Database/Schema Name)\n
        To access an additional host (production environment) set these variables and specify dev=False in the function call:\n
            PG_PROD_USER, PG_PROD_PASS, PG_PROD_HOST, PG_PROD_PORT, PG_PROD_DB\n

    Returns:
        postgres.Connection

    Note:
        Setting a variable equal to the function grants all psycopg2 functions (i.e. .cursor())

    Examples:        
        Set connection variable: connection = postgres_connection() \n
        Set cursor variable: cursor = connection.cursor()\n                   
        Save query results to dataframe: df = pd.read_sql_query(sqlQueryString, connection, parse_dates='post_date')
    """   
    
    # Pull Credentials where available
    # Lists below must all be in the same order
    lstVarNames = ['username', 'password', 'host', 'port', 'database']
    lstVars = [username, password, host, port, database] 
    lstDevEnvVars = [PG_DEV_USER, PG_DEV_PASS, PG_DEV_HOST, PG_DEV_PORT, PG_DEV_DB]
    lstProdEnvVars = [PG_PROD_USER, PG_PROD_PASS, PG_PROD_HOST, PG_PROD_PORT, PG_PROD_DB]
    
    # Logic to accept either the provided credentials, the production environment variables or the development environment variables based on function inputs
    dictArgs = {} 
    for name, var, prod, dev in zip(lstVarNames, lstVars, lstProdEnvVars, lstDevEnvVars):
        try:
            if var:                # If user has specified credentials choose these first
                dictArgs[name] = var
            elif devMode == False: # If user has requested production credentials use these next
                dictArgs[name] = prod
            elif devMode == True:  # Use default development credentials
                dictArgs[name] = dev
            else:                  # This should never execute but is a best practice catch-all
                raise TypeError('Insufficient credentials. Please specify username, password, host, port, and database name or add them to your system environment variables.')
        except: # Throw error if all credentials haven't been set
            raise TypeError('Insufficient credentials. Please specify username, password, host, port, and database name or add them to your system environment variables.')
        
    try: # Attempt Postgres connection with provided credentials
        postgres_connection = psycopg2.connect(
                                    user = dictArgs['username'],
                                    password = dictArgs['password'],
                                    host = dictArgs['host'],
                                    port = dictArgs['port'],
                                    database = dictArgs['database']
                                    )
        print('Connection successful.')
        return postgres_connection  
    except: # Raise error if the connection is unsuccessful 
        raise TypeError('Connection failed. Credentials disallowed.')


def postgres_query(sql:str, devMode: bool=True)->pd.DataFrame:
    """
    Summary:
        Function to query a given SQL string in Postgres and return results as a dataframe object
        Function will also print out query duration time in seconds
        
    Args:
        sql (string): A SQL query in string format (no ending ';' needed).
        devMode (boolean, optional): Defaults to True, if False Production database is used instead of development

    Returns:
        pandas.dataframe

    Example:        
        df = postgres_query(' SELECT * FROM PUBLIC.AUTH_USER ')
    """ 
    tic = time.perf_counter() # Start Timer
    
    connection = postgres_connection(devMode=devMode)  # Open Connection                     
    df = pd.read_sql_query(sql, connection, parse_dates='post_period') # Run Query export results to df
    if 'id' in df.columns:                             # Cleanup df format (for MEFS)
        df.drop('id', axis = 1, inplace = True)        
    connection.close()                                 # Close connection 
    
    toc = time.perf_counter() # End Timer and print time
    print(f"Query finished in {toc - tic:0.4f} seconds")
    
    return df


####################################################################################
## POSTGRES TABLE FUNCTIONS (CURRENTLY USED IN MONTH END FINANCIAL SUMMARY REPORT)
####################################################################################

def mk_table_df(strTableName:str)->pd.DataFrame:
    """
    Summary:
        Creates and runs a full table query on any postgres umbdb schema table entered\n
        Returns query results as a dataframe. Prints status and query duration as it runs   

    Args:
        strTableName (str): name of the postgres table you want to query\n
        usually '[app_name]_[model_name]' i.e. 'month_end_mefs_menu'
        
    Returns: 
        pandas.dataframe: All data in the given table as a df (minus the index)

    Example: 
        df = mk_table_df('month_end_mefs_menu')
    """
    print(f"Setting up and Running {strTableName} SQL Query...")
    strSQL = f"""
                select *
                from public.{strTableName}
             """ 
    df = postgres_query(strSQL)
    return df

def mk_menu_df()->pd.DataFrame:
    """ Creates SQL query for entire month_end_mefs_menu table """
    print('Setting up and Running Menu SQL Query...')
    strSQL = """select * from public.month_end_mefs_menu"""
    df = postgres_query(strSQL)
    df = df.sort_values(by='tab_order', ascending=True)
    df.rename(columns={'billing_prov_dwid': 'billing_provider_dwid'}, inplace=True)
    return df
    
def mk_fin_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_financialmetrics table 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running Financials SQL Query...')    
    strSQL = """
                 select * from analytics_site_db_financialmetrics
             """ 
    df = postgres_query(strSQL)

    # Setting Categorical variable columns to default to Other/Collection Fee (Not populated for bad debt payments)
    df[LST_CATG_VARIABLES] = df[LST_CATG_VARIABLES].fillna(value='OTHER/COLLECTION FEE') # This will remain here because its simpler than a ton of NVL()s in the SQL
    return df


def mk_fin_df_grp(strDwid)->pd.DataFrame:
    """ Creates a query for analytics_site_db_financialmetrics table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running Financials SQL Query...')    
    strSQL = """
                 select * from analytics_site_db_financialmetrics
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)

    # Setting Categorical variable columns to default to Other/Collection Fee (Not populated for bad debt payments)
    df[LST_CATG_VARIABLES] = df[LST_CATG_VARIABLES].fillna(value='OTHER/COLLECTION FEE') # This will remain here because its simpler than a ton of NVL()s in the SQL
    return df

def mk_gencnt_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_generalcounts table 
    """
    print('Setting up and Running General Counts SQL Query...')
    strSQL = """
                 select * from analytics_site_db_generalcounts
             """ 
    df = postgres_query(strSQL)
    return df

def mk_gencnt_df_grp(strDwid)->pd.DataFrame:
    """ Creates a query for analytics_site_db_generalcounts table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running General Counts SQL Query...')
    strSQL = """
                 select * from analytics_site_db_generalcounts
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)
    return df

def mk_ar_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_artrendreport table 
    """
    print('Setting up and Running AR SQL Query...')
    strSQL = """
                 select * from analytics_site_db_artrendreport
             """ 
    df = postgres_query(strSQL)
    # Truncing the post_period dates (3rd of the month etc.) to show only the first of the month
    df = df[df['post_period'] <= TRGTMON_YYYYMMDD] # Removing Current Month AR Numbers
    df = df[(df['current_financial_class_dwid'] != 883153)] # Removing null Financial classes and payor not found # DELETE - Shuktika is adding to dataset 
    # Combining any additional buckets
    df.loc[df['aging_bucket']=='121-150 DAYS', 'aging_bucket'] = '121-180 DAYS'
    df.loc[df['aging_bucket']=='151-180 DAYS', 'aging_bucket'] = '121-180 DAYS'
    return df

def mk_ar_df_grp(strDwid:str)->pd.DataFrame:
    """ Creates a query for analytics_site_db_artrendreport table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running AR SQL Query...')
    strSQL = """
                 select * from analytics_site_db_artrendreport
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)
    # Truncing the post_period dates (3rd of the month etc.) to show only the first of the month
    df = df[df['post_period'] <= TRGTMON_YYYYMMDD] # Removing Current Month AR Numbers
    df = df[(df['current_financial_class_dwid'] != 883153)] # Removing null Financial classes and payor not found # DELETE - Shuktika is adding to dataset 
    # Combining any additional buckets
    df.loc[df['aging_bucket']=='121-150 DAYS', 'aging_bucket'] = '121-180 DAYS'
    df.loc[df['aging_bucket']=='151-180 DAYS', 'aging_bucket'] = '121-180 DAYS'
    return df

def mk_lag_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_postlagmetrics table 
    """
    print('Setting up and Running Lag SQL Query...')
    strSQL = """
                 select * from analytics_site_db_postlagmetrics
             """ 
    df = postgres_query(strSQL)
    return df

def mk_lag_df_grp(strDwid:str)->pd.DataFrame:
    """ Creates a query for analytics_site_db_postlagmetrics table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running Lag SQL Query...')
    strSQL = """
                 select * from analytics_site_db_postlagmetrics
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)
    return df

def mk_asa_df():
    """ Creates a query for analytics_site_db_asaunits table 
    """
    print('Setting up and Running Asa SQL Query...')
    strSQL = """
                 select * from analytics_site_db_asaunits
             """ 
    df = postgres_query(strSQL)
    return df

def mk_asa_df_grp(strDwid:str)->pd.DataFrame:
    """ Creates a query for analytics_site_db_asaunits table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running Asa SQL Query...')
    strSQL = """
                 select * from analytics_site_db_asaunits
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)
    return df

def mk_dist_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_distributions table 
    """
    print('Setting up and Running Distributions SQL Query...')
    strSQL = """
                 select * from analytics_site_db_distributions
             """ 
    df = postgres_query(strSQL)
    return df

def mk_dist_df_grp(strDwid:str)->pd.DataFrame:
    """ Creates a query for analytics_site_db_distributions table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running Distributions SQL Query...')
    strSQL = """
                 select * from analytics_site_db_distributions
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)
    return df

def mk_edcensus_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_edcensus table 
    """
    print('Setting up and Running edcensus SQL Query...')
    strSQL = """
                 select * from analytics_site_db_edcensus
             """ 
    df = postgres_query(strSQL)
    return df

def mk_edcensus_df_grp(strDwid:str)->pd.DataFrame:
    """ Creates a query for analytics_site_db_edcensus table for one or more given billing_group_dwid's 
        strDwid: Takes a string of comma-seperated billing_group_dwids
    """
    print('Setting up and Running edcensus SQL Query...')
    strSQL = """
                 select * from analytics_site_db_edcensus
                 where billing_group_dwid in (""" + str(strDwid) + """)
             """ 
    df = postgres_query(strSQL)
    return df

def mk_arbotartrend_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_arbotartrend table 
    """
    print('Setting up and Running arTrend SQL Query...')
    strSQL = """
                select *
                from public.analytics_site_db_arbotartrend ar
                where ar.aging_bucket in ('180+ DAYS','91-120 DAYS', '121-150 DAYS', '151-180 DAYS')
             """ 
    df = postgres_query(strSQL)
    return df

def mk_arbotdenialtrend_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_artrend table 
    """
    print('Setting up and Running arTrend SQL Query...')
    strSQL = """
                select *
                from public.analytics_site_db_arbotdenialtrend 
             """ 
    df = postgres_query(strSQL)
    return df

def mk_arbotfinancialmetrics_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_arbotfinancialmetrics table 
    """
    print('Setting up and Running arTrend SQL Query...')
    strSQL = """
                select *
                from public.analytics_site_db_arbotfinancialmetrics
             """ 
    df = postgres_query(strSQL)
    return df

def mk_arbothundredpercentadjustments_df()->pd.DataFrame:
    """ Creates a query for analytics_site_db_arbothundredpercentadjustments table 
    """
    print('Setting up and Running arTrend SQL Query...')
    strSQL = """
                select *
                from public.analytics_site_db_arbothundredpercentadjustments
             """ 
    df = postgres_query(strSQL)
    return df


