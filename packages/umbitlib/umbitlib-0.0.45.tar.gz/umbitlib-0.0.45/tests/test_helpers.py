import unittest
import sqlalchemy as sa
from sqlalchemy import null
from src.umbitlib import helpers, dates
import pandas as pd
from datetime import date, datetime
import numpy as np
from pandera.errors import SchemaError
from dateutil.relativedelta import relativedelta
import calendar

# https://docs.python.org/3/library/unittest.html#assert-methods
# Based on the tutorial found here https://www.youtube.com/watch?v=6tNS--WetLI
# Test this file by running 'python -m unittest tests\test_helpers.py' in the terminal
# Name your test 'test_[function_name]_[functionality to test]'

####### !!! TROUBLESHOOTING TIPS FOR TESTS NOT REGISTERING  !!! #######
# Make sure imports are correct i.e. 'import src.umbitlib.helpers' instead of 'import helpers' in the function you're testing and everywhere else
# Make sure ALL libraries in the code file and the test file are installed in testing environment
# Make sure all test file's functions begin with 'test_' and classes begin with 'test'
# Test the test file manually by running 'python -m unittest tests\test_FILENAME.py' in the terminal to get more specific error output


class test_helpers(unittest.TestCase):
    
    # (Start) Example tests
    
    def test_add_success(self):
        """
        Test that 1 + 1 + 1 == 3
        """
        s = helpers.add(1,1,1)
        self.assertEqual(s, 3)
                
    def test_add_default(self): 
        """
        Test that third parameter defaults to 0 when not included
        i.e. 10 + 5 + 0 = 15
        """        
        self.assertEqual(helpers.add(10, 5), 15)
        
    def test_add_negative(self):
        """
        Test that -1 + 1 + 0 = 0
        """ 
        self.assertEqual(helpers.add(-1, 1, 0), 0)
        
    def test_add_double_negative(self):
        """
        Test that -1 + -1 + 0 = -2
        """
        self.assertEqual(helpers.add(-1, -1, 0), -2)
        
    def test_add_float(self):  
        """
        Test that float value throws TypeError
        """
        with self.assertRaises(TypeError):
            helpers.add(2.0, 1)    

    def test_add_type_error(self):
        """
        Test that q + 1 == TypeError
        """
        with self.assertRaises(TypeError):
            helpers.add("q",1)
            
    # (End) Example tests
    
    def test_up_down_success_up(self):
        """
        Test that 1000.01 and 1000 returns up
        """
        self.assertEqual(helpers.up_down(1000.01, 1000),'up')
        
    def test_up_down_success_down(self):
        """
        Test that 1000 and 1000.01 returns down
        """
        self.assertEqual(helpers.up_down(1000, 1000.01),'down')
    
    def test_up_down_equal(self):
        """
        Test that 1000 and 1000 return 'in-line with'
        """
        self.assertEqual(helpers.up_down(1000, 1000),'in-line with')
    
    def test_up_down_error(self):  
        """
        Test that float value throws TypeError
        """
        with self.assertRaises(TypeError):
            helpers.up_down('2.0', 1)    

    def test_evaluation_success_above(self):
        """
        Test that 1000.01 and 1000 returns dict with 'above'
        """
        self.assertEqual(helpers.evaluation(1001.01, 1000),{'value1': 1001.0, 'value2': 1000, 'val_delta': 1.0, 'val_up': 'above'})
        
    def test_evaluation_success_below(self):
        """
        Test that 1000 and 1001.01 returns dict with 'below'
        """
        self.assertEqual(helpers.evaluation(1000, 1001.01),{'value1': 1000, 'value2': 1001.0, 'val_delta': 1.0, 'val_up': 'below'})
    
    def test_evaluation_equal(self):
        """
        Test that 1000 and 1000 returns dict with 'in-line with'
        """
        self.assertEqual(helpers.evaluation(1000, 1000.00),{'value1': 1000, 'value2': 1000.0, 'val_delta': 0.0, 'val_up': 'in-line with'})
    
    def test_evaluation_error(self):  
        """
        Test that float value throws TypeError
        """
        with self.assertRaises(TypeError):
            helpers.evaluation('2.0', 1)   

    def test_cnt_unique(self):
        """
        Counts the number of current month current year rows in the dataframe
        """
        # Since the function this tests is a dynamically changing list of months
        # We need to create a dynamically changing dataframe with missing data
        # to make sure it doesn't error even if we don't have activity always
        lstMissingMonths = dates.LST_PFY_FYTD_MONTHS.copy()

        # Removing the last 6 months
        del lstMissingMonths[-6:]
        rowCount = len(lstMissingMonths)

        # Creating lists with monthly activity
        lstCharges =    [23856.56, 34009.58, 39800.23, 20400.98, 20000.23, 12202.23, 10021.45, 10021.45, 30021.23, 40021.67, 50021.87, 60021.97, 70021.23, 80021.12, 90021.36, 10020.12]
        lstVisitCnt =  [238, 340, 398, 204, 200, 122, 100, 100, 300, 400, 500, 600, 700, 800, 900, 100]
        lstCurFyFlg = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
        lstCurFyMonthFlg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

        # Paring down lists to match current dynamic month list
        lstCharges =    lstCharges[-rowCount:]
        lstVisitCnt =  lstVisitCnt[-rowCount:]
        lstCurFyFlg =  lstCurFyFlg[-rowCount:]
        lstCurFyMonthFlg =  lstCurFyMonthFlg[-rowCount:]

        # Creating dataframe using lists
        dfTest = pd.DataFrame(
            data={
                'post_period':pd.to_datetime(lstMissingMonths)
                , 'charges': lstCharges
                , 'visit_cnt': lstVisitCnt
                , 'cur_fy_flg': lstCurFyFlg
                , 'cur_fy_month_flg': lstCurFyMonthFlg
                }
        )
        self.assertEqual(helpers.cnt_unique(dfTest, 'visit_cnt', 'charges'), 1)
        
    def test_lst_metric_postperiods(self):
        """
        Tests that if the dataframe is missing months, missing months are assigned a value of 0
        """
        # Since the function this tests is a dynamically changing list of months
        # We need to create a dynamically changing dataframe with missing data
        # to make sure it doesn't error even if we don't have activity always
        lstMissingMonths = dates.LST_PFY_FYTD_MONTHS.copy()

        # Removing the last 6 months
        del lstMissingMonths[-6:]
        rowCount = len(lstMissingMonths)

        # Creating lists with monthly activity
        lstCharges =    [23856.56, 34009.58, 39800.23, 20400.98, 20000.23, 12202.23, 10021.45, 10021.45, 30021.23, 40021.67, 50021.87, 60021.97, 70021.23, 80021.12, 90021.36, 10020.12]
        lstVisitCnt =  [238, 340, 398, 204, 200, 122, 100, 100, 300, 400, 500, 600, 700, 800, 900, 100]
        lstCurFyFlg = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
        lstCurFyMonthFlg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

        # Paring down lists to match current dynamic month list
        lstCharges =    lstCharges[-rowCount:]
        lstVisitCnt =  lstVisitCnt[-rowCount:]
        lstCurFyFlg =  lstCurFyFlg[-rowCount:]
        lstCurFyMonthFlg =  lstCurFyMonthFlg[-rowCount:]

        # Creating dataframe using lists
        dfTest = pd.DataFrame(
            data={
                'post_period':pd.to_datetime(lstMissingMonths)
                , 'charges': lstCharges
                , 'visit_cnt': lstVisitCnt
                , 'cur_fy_flg': lstCurFyFlg
                , 'cur_fy_month_flg': lstCurFyMonthFlg
                }
        )
        srsResult = helpers.lst_metric_postperiods(dfTest, 'charges')
        # Checking that one of the missing months is 0
        self.assertEqual(srsResult[len(srsResult)-2], 0)    

    def test_lst_metric_postperiods_length(self):
        """
        Tests that the output length is equal to the current PFTYD number of months regardless of how many months have data
        """
        # Since the function this tests is a dynamically changing list of months
        # We need to create a dynamically changing dataframe with missing data
        # to make sure it doesn't error even if we don't have activity always
        lstMissingMonths = dates.LST_PFY_FYTD_MONTHS.copy()

        # Removing the last 6 months
        del lstMissingMonths[-6:]
        rowCount = len(lstMissingMonths)

        # Creating lists with monthly activity
        lstCharges =    [23856.56, 34009.58, 39800.23, 20400.98, 20000.23, 12202.23, 10021.45, 10021.45, 30021.23, 40021.67, 50021.87, 60021.97, 70021.23, 80021.12, 90021.36, 10020.12]
        lstVisitCnt =  [238, 340, 398, 204, 200, 122, 100, 100, 300, 400, 500, 600, 700, 800, 900, 100]
        lstCurFyFlg = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
        lstCurFyMonthFlg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

        # Paring down lists to match current dynamic month list
        lstCharges =    lstCharges[-rowCount:]
        lstVisitCnt =  lstVisitCnt[-rowCount:]
        lstCurFyFlg =  lstCurFyFlg[-rowCount:]
        lstCurFyMonthFlg =  lstCurFyMonthFlg[-rowCount:]

        # Creating dataframe using lists
        dfTest = pd.DataFrame(
            data={
                'post_period':pd.to_datetime(lstMissingMonths)
                , 'charges': lstCharges
                , 'visit_cnt': lstVisitCnt
                , 'cur_fy_flg': lstCurFyFlg
                , 'cur_fy_month_flg': lstCurFyMonthFlg
                }
        )
        srsResult = helpers.lst_metric_postperiods(dfTest, 'visit_cnt')
        self.assertEqual(len(srsResult), len(dates.LST_PFY_FYTD_MONTHS))    
    
    def test_days_in_month_30(self):
        """
        Tests a month with 30 days.
        """
        result = helpers.days_in_month(date(2022, 6, 1))
        self.assertEqual(result, 30)

    def test_days_in_month_31(self):
        """
        Tests a month with 30 days.
        """
        result = helpers.days_in_month(date(2022, 5, 1))
        self.assertEqual(result, 31)

    def test_days_in_month_28(self):
        """
        Tests a month with 28 days.
        """
        result = helpers.days_in_month(date.fromisoformat('2022-02-01'))
        self.assertEqual(result, 28)

    def test_days_in_month_29(self):
        """
        Tests a month with 29 days.
        """
        result = helpers.days_in_month(date.fromisoformat('2020-02-01'))
        self.assertEqual(result, 29)

    def test_days_in_month_error(self):
        """
        Tests an invalid input provided as date.
        """
        with self.assertRaises(TypeError):
            helpers.days_in_month('1-1-2022')

        with self.assertRaises(TypeError):
            helpers.days_in_month(20220101)

        with self.assertRaises(TypeError):
            helpers.days_in_month()

        with self.assertRaises(TypeError):
            helpers.days_in_month(None)
        
    def test_delta_positive_delta(self):
        """
        Tests for positive change
        """
        self.assertEqual(helpers.delta(8, 5, input_rounded=False),0.6000000000000001)


    def test_delta_output_round(self):
        """
        Tests rounding on output works correctly
        """
        self.assertEqual(helpers.delta(8, 5, input_rounded=False, output_rounded=True, output_decimals=1),0.6)


    def test_delta_input_round(self):
        """
        Tests rounding on input works correctly
        """
        self.assertEqual(helpers.delta(8.2, 4.8, input_rounded=True, input_decimals=0),0.6000000000000001)

    def test_delta_error(self):
        """
        Tests that string thows a TypeError
        """
        with self.assertRaises(TypeError):
            helpers.delta('8',5)
    def test_lst_metric_postperiods_empty_df(self):
        """
        Tests that the function still works when an empty dataframe is passed to it and that the result is an empty dataframe
        """
        emptyDf = pd.DataFrame(columns=['post_period','charges','visit_cnt' ,'cur_fy_flg','cur_fy_month_flg'])
        resultDf = helpers.lst_metric_postperiods(emptyDf, 'charges')
        self.assertEqual(resultDf.empty, emptyDf.empty)     

    def test_clean_division_valid_type(self):
        """
        Tests division with valid inputs for dividend and divisor
        """
        self.assertEqual(helpers.clean_division(45, 5), 9.0)

    def test_clean_division_divisor_zero(self):
        """
            Tests division when divisor is zero
        """
        self.assertEqual(helpers.clean_division(100, 0), 0.0)

    def test_clean_division_invalid_type(self):
        """
            Tests division with invalid types
        """
        with self.assertRaises(TypeError):
            helpers.clean_division('dividend', 1)
           

class TestTargetMonthTotalAR(unittest.TestCase):
    def setUp(self):
        target_month = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=1)
        previous_month = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=2)

        self.df_test = pd.DataFrame(
            data = {
                'post_period': [previous_month, previous_month, target_month, previous_month, target_month, target_month, target_month],
                'charges': [1000, 1200, 1500, 800, 500, 2000, 5000],
                'payments': [500, 600, 700, 400, 200, 900, 2000]
            }
        )

        self.df_test_invalid_column = pd.DataFrame(
            data = {
                'postperiod': [previous_month, previous_month, target_month, previous_month, target_month, target_month, target_month],
                'charges': [1000, 1200, 1500, 800, 500, 2000, 5000],
                'payments': [500, 600, 700, 400, 200, 900, 2000]
            }
        )

        self.df_test_missing_target_month = pd.DataFrame(
            data = {
                'post_period': [previous_month, previous_month, previous_month, previous_month, previous_month, previous_month, previous_month],
                'charges': [1000, 1200, 1500, 800, 500, 2000, 5000],
                'payments': [500, 600, 700, 400, 200, 900, 2000]
            }
        )

    def test_trgt_month_total_ar_valid_inputs(self):
        """
        Tests sum of desired metric for target post period
        """
        self.assertEqual(helpers.trgt_month_total_ar(self.df_test, 'charges'), 9000.0)


    def test_trgt_month_total_ar_no_records(self):
        """
        Tests sum of desired metric when records for target post period do not exist in the DataFrame
        """
        self.assertEqual(helpers.trgt_month_total_ar(self.df_test_missing_target_month, 'charges'), 0.0)


    def test_trgt_month_total_ar_invalid_type(self):
        """
            Tests calculation with invalid input types
        """
        with self.assertRaises(TypeError):
            helpers.trgt_month_total_ar('DataFrame', 'charges')

        with self.assertRaises(TypeError):
            helpers.trgt_month_total_ar(self.df_test, 100)


    def test_trgt_month_total_ar_invalid_column(self):
        """
            Tests calculation with invalid column names        
        """
        with self.assertRaises(KeyError):
            helpers.trgt_month_total_ar(self.df_test, 'charge_amt')

        with self.assertRaises(KeyError):
            helpers.trgt_month_total_ar(self.df_test_invalid_column, 'charges')


class TestTwelveMonthTotal(unittest.TestCase):
    def setUp(self):
        self.test_twelve_month_total = helpers.twelve_month_total
        self.test_df = pd.DataFrame(
            data={
                'post_period':['07/01/2020','08/01/2020','09/01/2020','10/01/2020','11/01/2020','12/01/2020','01/01/2021','02/01/2021','03/01/2021','04/01/2021','05/01/2021','06/01/2021','07/01/2021','08/01/2021','09/01/2021','11/01/2021']
                , 'charges':    [23856.56, 34009.58, 39800.23, 20400.98, 20000.23, 12202.23, 10021.45, 10021.45, 30021.23, 40021.67, 50021.87, 60021.97, 70021.23, 80021.12, 90021.36, 10020.12]
                , 'payments':  [238, 340, 398, 204, 200, 122, 100, np.nan, 300, 400, 500, 600, 700, 800, 900, 100]
                , 'proc_qty': [1, 1, 1, 'p', 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
                , 'wrvus': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
                }
        )
    
    def test_float_sum(self):
        """
        Test result of function equals the sum of dataframe using non-default vars
        """
        date_column = 'post_period'
        rolling_dates = ['07/01/2020','08/01/2020']
        metric = 'charges'
        sum = self.test_df[self.test_df[date_column].isin(rolling_dates)][metric].sum()
        self.assertEqual(self.test_twelve_month_total(object = self.test_df, metric=metric, date_column=date_column, rolling_dates=rolling_dates), sum)

    def test_int_sum(self):
        """
        Test sum of int values does not cause validation error of schema
        """
        sum = 238 + 340
        rolling_dates = ['07/01/2020','08/01/2020'] 
        metric = 'payments'
        self.assertEqual(self.test_twelve_month_total(object=self.test_df, metric=metric, rolling_dates=rolling_dates), sum)
    
    def test_invalid_dates(self):
        """
        Test dataframe schema date field.  Expects strings, not datetime, raises SchemaError
        """
        invalid_df = self.test_df
        invalid_df['post_period'] = pd.to_datetime(invalid_df['post_period'])
        with self.assertRaises(SchemaError):
            self.test_twelve_month_total(object=invalid_df, metric='charges')

    def test_invalid_numbers(self):
        """
        Test dataframe schema validation when column contains non-number, raises SchemaError
        """
        with self.assertRaises(SchemaError):
            self.test_twelve_month_total(object=self.test_df, metric='proc_qty')

class TestTwelveMonthAvg(unittest.TestCase): 

    def setUp(self):
        """
        Getting the dynamic list of months
        """
        lstMonths = dates.LST_13_MONTHS.copy()
        
        """
        13 months of valid data. Checks that it's using the correct months and calculating average correctly
        """
        self.dfTestSuccess = pd.DataFrame(
            data={
                'post_period':pd.to_datetime(lstMonths)
                , 'charges':    [100.1, 100.1, 100.1, 100.1, 100.1, 100.1, 100, 100, 100, 100, 100, 100, 200]
                }
        )

        """
        13 months of data with invalid (string) value in the df
        """
        self.dfTestFailure = pd.DataFrame(
                data={
                'post_period':pd.to_datetime(lstMonths)
                , 'charges':    ['data', 100.1, 100.1, 100.1, 100.1, 100.1, 100, 100, 100, 100, 100, 100, 200]
                }
        )
    
    def test_twelve_month_avg_success(self):
        self.assertEqual(helpers.twelve_month_avg(self.dfTestSuccess,'charges'), 100.05)
    
    def test_twelve_month_avg_type_error(self):
        with self.assertRaises(TypeError):
            helpers.twelve_month_avg(self.dfTestFailure,'charges')


class TestConvertSeconds(unittest.TestCase):

    def test_positive_seconds(self):
        # Test with positive seconds
        self.assertEqual(helpers.convert_seconds(3661), (0, 1, 1, 1))

    def test_zero_seconds(self):
        # Test with zero seconds
        self.assertEqual(helpers.convert_seconds(0), (0, 0, 0, 0))

    def test_seconds_to_days(self):
        # Test seconds conversion to days
        self.assertEqual(helpers.convert_seconds(3 * 24 * 3600), (3, 0, 0, 0))

    def test_seconds_to_hours(self):
        # Test seconds conversion to hours
        self.assertEqual(helpers.convert_seconds(5 * 3600), (0, 5, 0, 0))

    def test_seconds_to_minutes(self):
        # Test seconds conversion to minutes
        self.assertEqual(helpers.convert_seconds(180), (0, 0, 3, 0))

    def test_negative_seconds(self):
        # Test with negative seconds
        with self.assertRaises(ValueError):
            helpers.convert_seconds(-100)


class TestDataConversion(unittest.TestCase):

    def setUp(self):
        # Create a sample DataFrame for testing
        data = {
            'column1': ['1', '2', '3'],
            'column2': ['1.1', '2.2', '3.3'],
            'column3': ['True', 'False', 'True'],
            'column4': ['2023-01-01', '2023-02-02', '2023-03-03']
        }
        self.df = pd.DataFrame(data)

    def test_string_conversion(self):
        conversions = ['column1']
        converted_df = helpers.convert_data_types(self.df.copy(), conversions)
        self.assertTrue(converted_df['column1'].dtype == 'object')

    def test_int_conversion(self):
        conversions = [{'column1': 'int'}]
        converted_df = helpers.convert_data_types(self.df.copy(), conversions)
        self.assertTrue(converted_df['column1'].dtype == 'Int64')

    def test_float_conversion(self):
        conversions = [{'column2': 'float'}]
        converted_df = helpers.convert_data_types(self.df.copy(), conversions)
        self.assertTrue(converted_df['column2'].dtype == 'float64')

    def test_date_conversion(self):
        conversions = [{'column4': 'datetime'}]
        converted_df = helpers.convert_data_types(self.df.copy(), conversions)
        print(type(converted_df['column4']))
        self.assertTrue(converted_df['column4'].dtype == 'datetime64[ns]')

    def test_invalid_conversion(self):
        conversions = [{'nonexistent_column': 'int'}]
        with self.assertRaises(ValueError):
            helpers.convert_data_types(self.df.copy(), conversions)

    def test_unsupported_conversion(self):
        conversions = [{'column1': 'unsupported'}]
        with self.assertRaises(ValueError):
            helpers.convert_data_types(self.df.copy(), conversions)


class TestGenerateSqlAlchemyDtypes(unittest.TestCase):
    def test_integer_column(self):
        data = {'Age': [25, 30, 28]}
        df = pd.DataFrame(data)
        dtypes_dict = helpers.generate_sqlalchemy_dtypes(df)
        self.assertEqual(str(dtypes_dict['Age']), 'INTEGER')

    def test_float_column(self):
        data = {'Height': [160.5, 175.2, 162.0]}
        df = pd.DataFrame(data)
        dtypes_dict = helpers.generate_sqlalchemy_dtypes(df)
        self.assertEqual(str(dtypes_dict['Height']), 'FLOAT')

    def test_boolean_column(self):
        data = {'IsStudent': [True, False, False]}
        df = pd.DataFrame(data)
        dtypes_dict = helpers.generate_sqlalchemy_dtypes(df)
        self.assertEqual(str(dtypes_dict['IsStudent']), 'BOOLEAN')

    def test_string_column(self):
        data = {'Name': ['Alice', 'Bob', 'Charlie']}
        df = pd.DataFrame(data)
        dtypes_dict = helpers.generate_sqlalchemy_dtypes(df)
        self.assertEqual(str(dtypes_dict['Name']), 'VARCHAR(7)')

    def test_datetime_column(self):
        data = {'DateOfBirth': ['1995-01-15', '1992-06-20', '1997-09-05']}
        df = pd.DataFrame(data, dtype='datetime64[ns]')
        dtypes_dict = helpers.generate_sqlalchemy_dtypes(df)
        self.assertEqual(str(dtypes_dict['DateOfBirth']), 'TIMESTAMP')

    def test_unknown_column(self):
        data = {'Unknown': ['value1', 'value2', 'value3']}
        df = pd.DataFrame(data)
        dtypes_dict = helpers.generate_sqlalchemy_dtypes(df)
        self.assertEqual(str(dtypes_dict['Unknown']), 'VARCHAR(6)')