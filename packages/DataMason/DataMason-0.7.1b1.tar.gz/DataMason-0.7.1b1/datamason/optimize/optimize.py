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

from scipy.optimize import minimize, curve_fit, root

def optimize_minimize(fun, x0, **kwargs):
    try:
        """Minimization of scalar function of one or more variables."""
        return minimize(fun, x0, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def optimize_curve_fit(f, xdata, ydata, **kwargs):
    try:
        """Use non-linear least squares to fit a function, f, to data."""
        return curve_fit(f, xdata, ydata, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def optimize_root(fun, x0, **kwargs):
    try:
        """Find a root of a function."""
        return root(fun, x0, **kwargs)

    except Exception as e:
        print("An error occurred:", str(e))
        raise