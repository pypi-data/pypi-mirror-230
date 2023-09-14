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
import os

def test():
    
    print("Running DataMason test suite...")
    
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_suite_dir = os.path.join(current_dir, 'test_suite')
    
    # Discover all the test cases in the test_suite directory
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(test_suite_dir)

    # Run the test cases and print the results
    test_runner = unittest.TextTestRunner(verbosity=0)
    test_results = test_runner.run(test_suite)

    # Print summary
    print(f"\nRan {test_results.testsRun} tests with {len(test_results.failures)} failures and {len(test_results.errors)} errors.")
    
    # Print details of failed tests
    if test_results.failures:
        print("\nFailures:")
        for failure in test_results.failures:
            print(failure[0]) # Description of the failed test

    # Print details of errors
    if test_results.errors:
        print("\nErrors:")
        for error in test_results.errors:
            print(error[0]) # Description of the test with an error

    return test_results
