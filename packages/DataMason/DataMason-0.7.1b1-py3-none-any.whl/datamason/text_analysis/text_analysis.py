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

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer

def sent_tokenize_text(text, *args, **kwargs):
    try:
        """Sentence tokenize text."""
        return sent_tokenize(text, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def word_tokenize_text(text, *args, **kwargs):
    try:
        """Word tokenize text."""
        return word_tokenize(text, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def pos_tag_text(tokens, *args, **kwargs):
    try:
        """Part-of-speech tagging."""
        return pos_tag(tokens, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def freq_dist_text(tokens):
    try:
        """Frequency distribution of tokens."""
        return FreqDist(tokens)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def wordnet_lemmatizer():
    try:
        """Create a WordNet lemmatizer."""
        return WordNetLemmatizer()

    except Exception as e:
        print("An error occurred:", str(e))
        raise