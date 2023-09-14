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
import nltk
from datamason.text_analysis import text_analysis, pos_tag_text
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from unittest.mock import patch

try:
    # Download the tagger
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    print(f'Error downloading nltk tagger: {e}')



class TestFunctions(unittest.TestCase):

    def test_sent_tokenize_text(self):
        try:
            # Example text
            text = "This is a sentence. Here is another one."

            # Call the sent_tokenize_text function with the defined text
            result = text_analysis.sent_tokenize_text(text)

            # Expected result using NLTK's sent_tokenize function
            expected_result = sent_tokenize(text)

            # Assert that the result matches the expected sentence tokenization
            self.assertEqual(result, expected_result)

        except Exception as e:
            print("An error occurred:", str(e))
            raise
    def test_word_tokenize_text(self):
        try:
            # Example text
            text = "This is a sentence."

            # Call the word_tokenize_text function with the defined text
            result = text_analysis.word_tokenize_text(text)

            # Expected result using NLTK's word_tokenize function
            expected_result = word_tokenize(text)

            # Assert that the result matches the expected word tokenization
            self.assertEqual(result, expected_result)

        except Exception as e:
            print("An error occurred:", str(e))
            raise

    def test_pos_tag_text(self):
        try:
            # Example tokens
            tokens = ["apple", "banana", "orange"]
            
            # Mocking pos_tag to return dummy values
            with patch('nltk.tag.pos_tag', return_value=[('apple', 'NN'), ('banana', 'NN'), ('orange', 'NN')]):
                result = pos_tag_text(tokens)
            
            # Assert that the result matches the mocked return value
            self.assertEqual(result, [('apple', 'NN'), ('banana', 'NN'), ('orange', 'NN')])

        except Exception as e:
            print("An error occurred:", str(e))
            raise

    def test_freq_dist_text(self):
        try:
            # Example tokens
            tokens = ["apple", "banana", "apple", "orange", "banana", "apple"]

            # Call the freq_dist_text function with the defined tokens
            result = text_analysis.freq_dist_text(tokens)

            # Expected result using NLTK's FreqDist class
            expected_freq_dist = FreqDist(tokens)

            # Assert that the result matches the expected frequency distribution
            self.assertEqual(result, expected_freq_dist)

        except Exception as e:
            print("An error occurred:", str(e))
            raise
    def test_wordnet_lemmatizer(self):
        try:
            # Call the wordnet_lemmatizer function
            result = text_analysis.wordnet_lemmatizer()

            # Assert that the result is an instance of WordNetLemmatizer
            self.assertIsInstance(result, WordNetLemmatizer)

        except Exception as e:
            print("An error occurred:", str(e))
            raise