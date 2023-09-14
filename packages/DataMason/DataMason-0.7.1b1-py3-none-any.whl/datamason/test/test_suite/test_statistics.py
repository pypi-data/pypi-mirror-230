#     Copyright (c) 2023, Kevan White (Thyripian)
#     All rights reserved.

#     Redistribution and use in source and binary forms, with or without
#     modification, are permitted provided that the following conditions are met:
#       Compliance with MIT License clauses.

#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#     AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#     IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#     FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#     DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#     SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#     CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#     OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#     OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import statsmodels.api as sm
from statsmodels.api import add_constant
from scipy.stats import ttest_ind, chisquare
from statsmodels.formula.api import ols, logit, glm
import numpy as np
from datamason.statistics import *
from scipy.stats import linregress
from numpy.random import seed, rand, randn
from numpy import column_stack


class TestFunctions(unittest.TestCase):

    def test_linregress_statistics(self):
        try:
            # Testing with valid input
            x = np.array([1, 2, 3, 4])
            y = np.array([2, 4, 6, 8])
            result = statistics.linregress_statistics(x, y)
            expected_result = linregress(x, y)
            assert result == expected_result, f"Expected {expected_result}, got {result}"

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_ttest_ind_statistics(self):
        try:
            # Example independent samples
            a = np.array([10, 20, 30, 40])
            b = np.array([5, 15, 25, 35])

            # Call the ttest_ind_statistics function with the defined a and b
            result = statistics.ttest_ind_statistics(a, b)

            # Expected result using SciPy's ttest_ind function
            expected_t_statistic, expected_p_value = ttest_ind(a, b)

            # Assert that the result matches the expected t-statistic and p-value
            self.assertAlmostEqual(result.statistic, expected_t_statistic, places=5)
            self.assertAlmostEqual(result.pvalue, expected_p_value, places=5)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_chisquare_statistics(self):
        try:
            # Generate observed and expected frequencies
            observed_values = np.array([10, 20, 30, 40])
            expected_values = np.array([12, 18, 28, 42])
            
            # Validate that they match within the required tolerance
            tolerance = 1e-8
            if np.abs(np.sum(observed_values) - np.sum(expected_values)) > tolerance:
                self.fail("The sum of observed and expected frequencies must match within a tolerance of 1e-8")
            
            # Run the function under test
            result_stat, result_p_value = chisquare_statistics(observed_values, expected_values)
            
            # Run the original scipy function to get expected results
            expected_stat, expected_p_value = chisquare(observed_values, expected_values)
            
            # Assertions to compare the function output against expected results
            self.assertAlmostEqual(result_stat, expected_stat, places=7, msg="Chi-Square statistic does not match expected value.")
            self.assertAlmostEqual(result_p_value, expected_p_value, places=7, msg="P-value does not match expected value.")
        
        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_ols_statistics(self):
        try:
            # Creating a simple dataset where y = 3 + 2 * x1 + 3 * x2
            np.random.seed(42) # for reproducibility
            x1 = np.random.rand(100)
            x2 = np.random.rand(100)
            y = 3 + 2 * x1 + 3 * x2 + np.random.randn(100) * 0.1 # adding some random noise

            # Call the ols_statistics function directly
            result = statistics.ols_statistics(y, sm.add_constant(np.column_stack((x1, x2))))


            # Assert that the estimated coefficients are close to the true coefficients
            self.assertAlmostEqual(result.params[0], 3, delta=0.5, msg="Intercept not as expected")
            self.assertAlmostEqual(result.params[1], 2, delta=0.5, msg="Coefficient for x1 not as expected")
            self.assertAlmostEqual(result.params[2], 3, delta=0.5, msg="Coefficient for x2 not as expected")


        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_logit_statistics(self):
        try:
            # Generating a well-conditioned dataset for logistic regression
            np.random.seed(42)  # for reproducibility
            x1 = np.linspace(0, 1, 500)  # Evenly spaced values between 0 and 1, increased sample size

            # Generating binary outcome variable y with clearer separation
            # Using a logistic function to generate probabilities
            prob = 1 / (1 + np.exp(- (3 + 2 * x1)))

            # Generating y based on probabilities
            y = np.random.binomial(1, prob)

            # Adding a constant term for the intercept
            X = np.column_stack((np.ones(len(x1)), x1))

            # Running the function under test
            result = logit_statistics(y, X)

            # Check for error message
            if result.error_message:
                self.fail(f"An unexpected error occurred: {result.error_message}")

            # Existing assertions
            estimated_coef = result.params
            self.assertIsNotNone(result, "Result should not be None")
            self.assertAlmostEqual(estimated_coef[0], 3, delta=1, msg="Intercept not as expected")
            self.assertAlmostEqual(estimated_coef[1], 2, delta=0.5, msg="Coefficient for x1 not as expected")

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_glm_statistics(self):
        try:
            # Creating a simple dataset where y = 3 + 2 * x1 + 3 * x2
            np.random.seed(42) # for reproducibility
            x1 = np.random.rand(100)
            x2 = np.random.rand(100)
            y = 3 + 2 * x1 + 3 * x2 + np.random.randn(100) * 0.1 # adding some random noise

            # Call the glm_statistics function directly
            result = statistics.glm_statistics(y, sm.add_constant(np.column_stack((x1, x2))))

            # Assert that the estimated coefficients are close to the true coefficients
            self.assertAlmostEqual(result.params[0], 3, places=1) # Intercept
            self.assertAlmostEqual(result.params[1], 2, places=1) # Coefficient for x1
            self.assertAlmostEqual(result.params[2], 3, delta=0.1)  # Coefficient for x2

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_ttest_ind_statistics(self):
        try:
            a = [1, 2, 3]
            b = [4, 5, 6]
            result = statistics.ttest_ind_statistics(a, b)
            assert result is not None, "Result should not be None"

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_arima_statistics(self):
        try:
            data = [1, 2, 3, 4, 5, 6]
            result = statistics.arima_statistics(data, order=(1, 0, 0))
            assert result is not None, "Result should not be None"

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")