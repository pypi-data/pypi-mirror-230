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
import numpy as np
from datamason.preprocessing import prepare, transform

class TestFunctions(unittest.TestCase):

    def test_fillna(self):
        try:
            data = pd.DataFrame({'A': [1, np.nan], 'B': [3, 4]})
            filled_data = prepare.fillna(data, value=2)
            assert filled_data.loc[1, 'A'] == 2

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_drop_duplicates(self):
        try:
            data = pd.DataFrame({'A': [1, 1], 'B': [3, 3]})
            unique_data = prepare.drop_duplicates(data)
            assert unique_data.shape[0] == 1

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_merge(self):
        try:
            data1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            data2 = pd.DataFrame({'C': [5, 6], 'D': [7, 8]})
            merged_data = transform.merge(data1, data2, left_index=True, right_index=True)
            assert merged_data.shape == (2, 4)

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_groupby(self):
        try:
            data = pd.DataFrame({'A': [1, 1], 'B': [3, 4]})
            grouped_data = transform.groupby(data, 'A').sum()
            assert grouped_data.loc[1, 'B'] == 7

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_pivot_table(self):
        try:
            data = pd.DataFrame({'A': [1, 1], 'B': [2, 2], 'C': [3, 4]})
            pivot_data = transform.pivot_table(data, values='C', index='A', columns='B', aggfunc='sum')
            assert pivot_data.loc[1, 2] == 7

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_cut(self):
        try:
            data = pd.Series([1, 2, 3, 4])
            cut_data = transform.cut(data, bins=2)
            assert cut_data.cat.categories[0] == pd.Interval(0.997, 2.5, closed='right')

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_get_dummies(self):
        try:
            data = pd.DataFrame({'A': ['a', 'b'], 'B': [3, 4]})
            dummies_data = transform.get_dummies(data, columns=['A'])
            assert 'A_a' in dummies_data.columns
            assert 'A_b' in dummies_data.columns

            data = pd.DataFrame({'A': [1, 1], 'B': [3, 4], 'C': [5, 6]})
            pivot_data = transform.pivot_table(data, values='C', index='A', columns='B', aggfunc='sum')
            assert pivot_data.loc[1, 3] == 5
            assert pivot_data.loc[1, 4] == 6

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_cut(self):
        try:
            data = pd.Series([1, 2, 3, 4])
            cut_data = prepare.cut(data, bins=[0, 2, 4], labels=['Low', 'High'])
            assert cut_data[0] == 'Low'
            assert cut_data[3] == 'High'

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")
            
    def test_get_dummies(self):
        try:
            data = pd.DataFrame({'A': ['a', 'b'], 'B': [3, 4]})
            dummies_data = transform.get_dummies(data, columns=['A'])
            assert 'A_a' in dummies_data.columns
            assert 'A_b' in dummies_data.columns

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")