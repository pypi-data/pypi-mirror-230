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

def accuracy_score_metrics(y_true, y_pred, *args, **kwargs):
    try:
        """Accuracy classification score."""
        return accuracy_score(y_true, y_pred, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def mean_squared_error_metrics(y_true, y_pred, *args, **kwargs):
    try:
        """Mean squared error regression loss."""
        return mean_squared_error(y_true, y_pred, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def confusion_matrix_metrics(y_true, y_pred, *args, **kwargs):
    try:
        """Compute confusion matrix to evaluate the accuracy of a classification."""
        return confusion_matrix(y_true, y_pred, *args, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise