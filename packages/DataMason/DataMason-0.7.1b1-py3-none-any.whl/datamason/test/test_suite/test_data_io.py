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
import os
from datamason.data_io import io as data_io

class TestFunctions(unittest.TestCase):

    def test_read_csv(self):
        try:
            # Relative path to the test CSV file in the same directory as the test
            test_csv_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')

            # Create a sample DataFrame
            df = pd.DataFrame({
                'Name': ['Alice', 'Bob'],
                'Age': [28, 22]
            })

            # Save the DataFrame to the test CSV file
            df.to_csv(test_csv_path, index=False)

            # Read the CSV file using the function being tested
            data = data_io.read_csv(test_csv_path)

            assert isinstance(data, pd.DataFrame)

            # Remove the test CSV file after the test
            os.remove(test_csv_path)
            
        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")