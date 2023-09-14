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
from datamason.validation import validate

class TestFunctions(unittest.TestCase):

    def test_data(self):
        try:
            # Test with invalid type data
            df_invalid_type = pd.DataFrame({'A': [1, '2', 3]})
            rules_valid = {'A': {'type': int, 'min_value': 1, 'max_value': 3}}

            errors_invalid_type_1, errors_out_of_range_1 = validate.data(df_invalid_type, rules_valid)

            # Updated test assertion
            self.assertTrue(any(err.startswith("Type mismatch in column 'A'") for err in errors_invalid_type_1))

            # Test with out-of-range data
            df_out_of_range = pd.DataFrame({'A': [0, 1, 4]})
            errors_invalid_type_2, errors_out_of_range_2 = validate.data(df_out_of_range, rules_valid)
            self.assertTrue("Value out of range in column 'A' at index 0" in errors_out_of_range_2)

            # Test with missing column
            df_missing_col = pd.DataFrame({'B': [1, 2, 3]})
            errors_invalid_type_3, errors_out_of_range_3 = validate.data(df_missing_col, rules_valid)
            self.assertTrue("Column 'A' not found in DataFrame" in errors_invalid_type_3)

            # Test with valid data
            df_valid = pd.DataFrame({'A': [1, 2, 3]})
            errors_invalid_type_4, errors_out_of_range_4 = validate.data(df_valid, rules_valid)
            self.assertEqual(errors_invalid_type_4, [])
            self.assertEqual(errors_out_of_range_4, [])

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")