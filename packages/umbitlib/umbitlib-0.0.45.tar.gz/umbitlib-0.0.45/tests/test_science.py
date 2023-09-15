import unittest
from src.umbitlib import science
# https://docs.python.org/3/library/unittest.html#assert-methods
# Based on the tutorial found here https://www.youtube.com/watch?v=6tNS--WetLI
# Test this file by running 'python -m unittest tests\test_science.py' in the terminal
# Use the naming convention: 'test_[function_name]_[functionality to test]'

class test_science(unittest.TestCase):
    
    def test_p_pass_fail_defaultmore(self):
        """
        Test that .06 passes
        """
        result = science.p_pass_fail(.06)
        self.assertEqual(result, "[PASSED] ")
        
    def test_p_pass_fail_less(self):
        """
        Test that .03 fails compared to .04
        """
        result = science.p_pass_fail(.03, .04)
        self.assertEqual(result, "[FAILED] ")
        
    def test_p_pass_fail_more(self):
        """
        Test that .10 passes compared to .08
        """
        result = science.p_pass_fail(.10, .08)
        self.assertEqual(result, "[PASSED] ")
        
    def test_p_pass_fail_typeerror(self):  
        """
        Test string value throws TypeError
        """
        with self.assertRaises(TypeError):
            science.p_pass_fail('string')
                
    def test_p_pass_fail_typeerror2(self):  
        """
        Test second input value throws TypeError
        """
        with self.assertRaises(TypeError):
            science.p_pass_fail(1, 'string') 
        
    def test_z_pass_fail_defaultmore(self):
        """
        Test that 1.97 passes
        """
        result = science.z_pass_fail(1.95)
        self.assertEqual(result, "[PASSED] ")
        
    def test_z_pass_fail_less(self):
        """
        Test that -2.01 fails compared to 2
        """
        result = science.z_pass_fail(-2.01, 2)
        self.assertEqual(result, "[FAILED] ")
        
    def test_z_pass_fail_more(self):
        """
        Test that 1 passes compared to 2.01
        """
        result = science.z_pass_fail(1, 2.01)
        self.assertEqual(result, "[PASSED] ")
        
    def test_z_pass_fail_typeerror(self):  
        """
        Test string value throws TypeError
        """
        with self.assertRaises(TypeError):
            science.z_pass_fail('string') 

    def test_z_pass_fail_typeerror2(self):  
        """
        Test second input value throws TypeError
        """
        with self.assertRaises(TypeError):
            science.z_pass_fail(1, 'string') 

    