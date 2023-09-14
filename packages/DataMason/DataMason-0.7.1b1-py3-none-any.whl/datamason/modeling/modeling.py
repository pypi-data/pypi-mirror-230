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

from sklearn.model_selection import train_test_split
from sklearn.svm import SVC, SVR
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.naive_bayes import GaussianNB

def train_test_split_model(*arrays, **kwargs):
    try:
        """Split arrays or matrices into random train and test subsets."""
        return train_test_split(*arrays, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def SVC_model(**kwargs):
    try:
        """C-Support Vector Classification."""
        return SVC(**kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def RandomForestClassifier_model(**kwargs):
    try:
        """A random forest classifier."""
        return RandomForestClassifier(**kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def KNeighborsClassifier_model(**kwargs):
    try:
        """Classifier implementing the k-nearest neighbors vote."""
        return KNeighborsClassifier(**kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def cross_val_score_model(estimator, X, y, **kwargs):
    try:
        """Evaluate a score by cross-validation."""
        return cross_val_score(estimator, X, y, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def GridSearchCV_model(estimator, param_grid, **kwargs):
    try:
        """Exhaustive search over a specified parameter grid."""
        return GridSearchCV(estimator, param_grid, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def GaussianNB_model(**kwargs):
    try:
        """Gaussian Naive Bayes (GaussianNB)"""
        return GaussianNB(**kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def SVR_model(**kwargs):
    try:
        """Epsilon-Support Vector Regression."""
        return SVR(**kwargs)
    except Exception as e:
        print("An error occurred:", str(e))
        raise

# tensorflow/keras functions
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, LSTM

def Sequential_model(layers):
    try:
        """Linear stack of layers."""
        model = Sequential()
        for layer in layers:
            model.add(layer)
        return model

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def Dense_layer(units, **kwargs):
    try:
        """Regular densely-connected Neural Network (NN) layer."""
        return Dense(units, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def Conv2D_layer(filters, kernel_size, **kwargs):
    try:
        """2D convolution layer (e.g. spatial convolution over images)."""
        return Conv2D(filters, kernel_size, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def LSTM_layer(units, **kwargs):
    try:
        """Long Short-Term Memory layer - Hochreiter 1997."""
        return LSTM(units, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def compile_model(model, **kwargs):
    try:
        """Configures the model for training."""
        model.compile(**kwargs)
        return model

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def fit_model(model, x, y, **kwargs):
    try:
        """Trains the model for a fixed number of epochs (iterations on a dataset)."""
        return model.fit(x, y, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def evaluate_model(model, x, y, **kwargs):
    try:
        """Returns the loss value & metrics values for the model in test mode."""
        return model.evaluate(x, y, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise