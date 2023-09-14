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

import pandas as pd

def fillna(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
    try:
        return df.fillna(value=value, method=method, axis=axis, inplace=inplace, limit=limit, downcast=downcast)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def drop_duplicates(df, subset=None, keep='first', inplace=False, ignore_index=False):
    try:
        return df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)


    except Exception as e:
        print("An error occurred:", str(e))
        raise

def cut(series, bins, right=True, labels=None, retbins=False, precision=3, include_lowest=False, duplicates='raise'):
    try:
        return pd.cut(series, bins, right=right, labels=labels, retbins=retbins, precision=precision, include_lowest=include_lowest, duplicates=duplicates)
    except Exception as e:
        print("An error occurred:", str(e))
        raise
