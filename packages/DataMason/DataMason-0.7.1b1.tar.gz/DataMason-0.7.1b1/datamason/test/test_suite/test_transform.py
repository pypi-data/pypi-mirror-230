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
import pandas as pd
from datamason.preprocessing import transform
import numpy as np
import warnings

class TestFunctions(unittest.TestCase):

    def test_merge(self):
        try:
            left = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            right = pd.DataFrame({'A': [1, 3], 'C': [5, 6]})
            result = transform.merge(left, right, on='A')
            expected_result = pd.merge(left, right, on='A')
            pd.testing.assert_frame_equal(result, expected_result)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_groupby(self):
        try:
            data = pd.DataFrame({'A': [1, 1, 2], 'B': [4, 5, 6]})
            result = transform.groupby(data, by='A').sum()
            expected_result = data.groupby(by='A').sum()
            pd.testing.assert_frame_equal(result, expected_result)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_pivot_table(self):
        try:
            data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
            result = transform.pivot_table(data, values='C', index='A', columns='B')
            expected_result = pd.pivot_table(data, values='C', index='A', columns='B')
            pd.testing.assert_frame_equal(result, expected_result)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_cut(self):
        try:
            x = [1, 2, 3, 4, 5]
            bins = [1, 3, 5]
            result = transform.cut(x, bins)
            expected_result = pd.cut(x, bins)
            # Cast the Categorical objects to pd.Series before comparison
            pd.testing.assert_series_equal(pd.Series(result), pd.Series(expected_result))
        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_get_dummies(self):
        try:
            data = pd.DataFrame({'A': ['a', 'b', 'a'], 'B': [1, 2, 3]})
            result = transform.get_dummies(data, columns=['A'])
            expected_result = pd.get_dummies(data, columns=['A'])
            pd.testing.assert_frame_equal(result, expected_result)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_transpose(self):
        try:
            data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            result = transform.transpose(data)
            expected_result = data.transpose()
            pd.testing.assert_frame_equal(result, expected_result)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_PCA_transform(self):
        try:
            data = np.array([[1, 2], [3, 4], [5, 6]])
            result = transform.PCA_transform(data, n_components=2)
            assert result is not None, "Result should not be None"

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_OneHotEncoder_transform(self):
        try:
            data = [['cat'], ['dog'], ['cat']]
            result = transform.OneHotEncoder_transform(data)
            assert result is not None, "Result should not be None"

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_SelectKBest_transform(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            try:
                data = np.array([[1, 2], [3, 4], [5, 6]])
                target = [1, 2, 3]
                result = transform.SelectKBest_transform(data, target, k=2)
                assert result is not None, "Result should not be None"
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_StandardScaler_transform(self):
        try:
            data = np.array([[1, 2], [3, 4], [5, 6]])
            result = transform.StandardScaler_transform(data)
            assert result is not None, "Result should not be None"

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            