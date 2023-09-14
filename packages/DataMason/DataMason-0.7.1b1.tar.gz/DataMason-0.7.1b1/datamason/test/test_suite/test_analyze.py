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
from datamason.analysis import analysis

class TestFunctions(unittest.TestCase):

    def test_summarize(self):
        try:
            data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            summary = analysis.summarize(data)
            assert isinstance(summary, dict)
            assert summary['A']['mean'] == 1.5
            assert summary['B']['mean'] == 3.5  # Corrected the way 'mean' value is accessed for column 'B'

        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")

    def test_find_correlations(self):
        try:
            data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            correlations = analysis.find_correlations(data)
            assert isinstance(correlations, pd.DataFrame)
        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")