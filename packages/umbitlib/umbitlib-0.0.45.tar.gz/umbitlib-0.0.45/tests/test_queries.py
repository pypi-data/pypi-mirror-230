import unittest 

from src.umbitlib import queries
import psycopg2
import pandas as pd
import time
from openpyxl import load_workbook
import cx_Oracle


# https://docs.python.org/3/library/unittest.html#assert-methods
# Based on the tutorial found here https://www.youtube.com/watch?v=6tNS--WetLI
# Test this file by running 'python -m unittest tests\test_queries.py' in the terminal
# Name your test 'test_[function_name]_[functionality to test]'

class test_queries(unittest.TestCase):
    
    def test_postgres_connection_created(self):
        """
        Test that a connection object is successfully created
        """
        conn = queries.postgres_connection()
        self.assertIsNotNone(conn)
        
    def test_postgres_query_table(self):
        """
        Test that PUBLIC.HUB_ACTION table query returns correct data
        """
        query = """
                SELECT *
                FROM PUBLIC.HUB_ACTION
                WHERE ACTION_ID = 3001
                """

        df = queries.postgres_query(query)
        self.assertEqual(df['action_name'][0], 'Created')
    
    def test_oracle_connection_created(self):
        """
        Test that a connection object is successfully created
        """
        conn = queries.oracle_connection()
        self.assertIsNotNone(conn)
    
    def test_oracle_connection_is_oracle(self):
        """
        Test that the created connection object is an oracle connection
        """
        conn = queries.oracle_connection()
        self.assertIsInstance(conn, cx_Oracle.Connection)
        
        
    def test_oracle_query_zc_state(self):
        """
        Test that CLARITY_ORG.ZC_STATE table query returns correct data
        """
        query = """
                SELECT NAME
                FROM CLARITY_REPORT.ZC_STATE
                WHERE ABBR = 'AK'
                """
        df = queries.oracle_query(query)
        self.assertEqual(df['NAME'][0], 'Alaska')
        
                
if __name__ == '__main__':
    unittest.main()