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

import statsmodels.api as sm
from scipy.stats import linregress, ttest_ind, chisquare
from statsmodels.stats.outliers_influence import variance_inflation_factor
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
from numpy.linalg import LinAlgError
from statsmodels.tools.tools import add_constant


def linregress_statistics(x, y):
    try:
        """Calculate a linear least-squares regression."""
        return linregress(x, y)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def ttest_ind_statistics(a, b, *args, **kwargs):
    try:
        """Calculate the T-test for the means of two independent samples."""
        return ttest_ind(a, b, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def chisquare_statistics(f_obs, f_exp=None, *args, **kwargs):
    try:
        """Calculate a one-way chi-square test."""
        return chisquare(f_obs, f_exp, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise

def ols_statistics(endog, exog, regularization=None, alpha=1.0, *args, **kwargs):
    try:
        # Data Checks
        if endog is None or exog is None:
            raise ValueError("Endogenous or exogenous variables cannot be None.")
        
        # Convert to DataFrame if it's a numpy array
        if isinstance(exog, np.ndarray):
            exog = pd.DataFrame(exog, columns=[f'X{i}' for i in range(exog.shape[1])])

        # Check for multicollinearity using VIF
        vif_data = pd.DataFrame()
        vif_data["feature"] = exog.columns
        vif_data["VIF"] = [variance_inflation_factor(exog.values, i) for i in range(len(exog.columns))]

        
        if vif_data["VIF"].max() > 10:
            print("Warning: High multicollinearity detected.")
        
        # Regularization
        if regularization == 'ridge':
            return sm.OLS(endog, exog, *args, **kwargs).fit_regularized(alpha=alpha, L1_wt=0)
        elif regularization == 'lasso':
            return sm.OLS(endog, exog, *args, **kwargs).fit_regularized(alpha=alpha, L1_wt=1)
        else:
            return sm.OLS(endog, exog, *args, **kwargs).fit()
    except Exception as e:
        print("An error occurred:", str(e))
        raise

class LogitResult:
    def __init__(self, params=None, error_message=None):
        self.params = params
        self.error_message = error_message

def logit_statistics(endog, exog, *args, **kwargs):
    try:
        # Data Checks
        if endog is None or exog is None:
            raise ValueError("Endogenous or exogenous variables cannot be None.")
        
        if not isinstance(exog, pd.DataFrame):
            exog = pd.DataFrame(exog, columns=[f'X{i}' for i in range(exog.shape[1])])

        # Check for multicollinearity using VIF
        vif_data = pd.DataFrame()
        vif_data["feature"] = exog.columns  
        vif_data["VIF"] = [variance_inflation_factor(exog.values, i) for i in range(len(exog.columns))]
        
        if vif_data["VIF"].max() > 10:
            print("Warning: High multicollinearity detected.")
        
        model_fit = sm.Logit(endog, exog, *args, **kwargs).fit()
        return LogitResult(params=model_fit.params)
    except LinAlgError:
        return LogitResult(error_message="Singular matrix detected. Consider removing highly correlated variables or using regularization.")
    except Exception as e:
        return LogitResult(error_message=str(e))

def glm_statistics(endog, exog, family=None, *args, **kwargs):
    try:
        """Generalized Linear Model (GLM)."""
        return sm.GLM(endog, exog, family, *args, **kwargs).fit()

    except Exception as e:
        print("An error occurred:", str(e))
        raise

def arima_statistics(endog, order, **kwargs):
    try:
        return sm.tsa.ARIMA(endog, order=order).fit(**kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
