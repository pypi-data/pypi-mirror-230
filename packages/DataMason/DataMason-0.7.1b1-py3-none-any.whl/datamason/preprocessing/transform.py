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
from sklearn.preprocessing import OneHotEncoder
from sklearn.exceptions import NotFittedError
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import StandardScaler
import numpy as np
import warnings


def merge(left, right, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=True, indicator=False, validate=None):
    try:
        return pd.merge(left, right, how, on, left_on, right_on, left_index, right_index, sort, suffixes, copy, indicator, validate)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def groupby(df, by=None, axis=0, level=None, as_index=True, sort=True, group_keys=True, squeeze=False, observed=False):
    try:
        return df.groupby(by, axis, level, as_index, sort, group_keys, squeeze, observed)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def pivot_table(df, values=None, index=None, columns=None, aggfunc='mean', fill_value=None, margins=False, dropna=True, margins_name='All', observed=False):
    try:
        return pd.pivot_table(df, values, index, columns, aggfunc, fill_value, margins, dropna, margins_name, observed)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def cut(x, bins, right=True, labels=None, retbins=False, precision=3, include_lowest=False, duplicates='raise'):
    try:
        return pd.cut(x, bins, right, labels, retbins, precision, include_lowest, duplicates)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def get_dummies(df, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None):
    try:
        return pd.get_dummies(df, prefix, prefix_sep, dummy_na, columns, sparse, drop_first, dtype)

    except Exception as e:
        print("An error occurred:", str(e))
        raise

def OneHotEncoder_transform(data):
    try:
        encoder = OneHotEncoder(sparse_output=False)  # Explicitly set sparse_output to False to supress future warning
        transformed_data = encoder.fit_transform(data)
        return transformed_data
    except NotFittedError as e:
        raise ValueError("The data could not be fitted: " + str(e))
    except Exception as e:
        raise RuntimeError("An unexpected error occurred: " + str(e))

def PCA_transform(data, n_components):
    try:
        pca = PCA(n_components=n_components)
        transformed_data = pca.fit_transform(data)
        return transformed_data
    except NotFittedError as e:
        raise ValueError("The data could not be fitted: " + str(e))
    except Exception as e:
        raise RuntimeError("An unexpected error occurred: " + str(e))

def SelectKBest_transform(data, target, k):
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
        # Check for NaN or infinity in the data
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ValueError("Data contains NaN or infinity, which is not supported.")

        selector = SelectKBest(score_func=f_classif, k=k)
        transformed_data = selector.fit_transform(data, target)
        return transformed_data
    except NotFittedError as e:
        raise ValueError("The data could not be fitted: " + str(e))
    except Exception as e:
        raise RuntimeError("An unexpected error occurred: " + str(e))

def StandardScaler_transform(data):
    try:
        scaler = StandardScaler()
        transformed_data = scaler.fit_transform(data)
        return transformed_data
    except NotFittedError as e:
        raise ValueError("The data could not be fitted: " + str(e))
    except Exception as e:
        raise RuntimeError("An unexpected error occurred: " + str(e))

def transpose(data):
    try:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")
        return data.transpose()
    except Exception as e:
        raise RuntimeError("An unexpected error occurred: " + str(e))
