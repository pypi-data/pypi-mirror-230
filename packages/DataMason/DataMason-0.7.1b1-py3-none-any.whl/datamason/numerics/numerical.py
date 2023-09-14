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

import numpy as np

def array(object, dtype=None, copy=True, order='K', subok=False, ndmin=0):
    try:
        return np.array(object, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=ndmin)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0):
    try:
        return np.linspace(start, stop, num, endpoint, retstep, dtype, axis)
    except Exception as e:
        print("An error occurred:", str(e))
        raise
def arange(start=None, stop=None, step=1, dtype=None):
    try:
        return np.arange(start, stop, step, dtype)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def reshape(a, newshape, order='C'):
    try:
        return np.reshape(a, newshape, order)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def dot(a, b, out=None):
    try:
        return np.dot(a, b, out)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def concatenate(arrays, axis=0, out=None):
    try:
        return np.concatenate(arrays, axis, out)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def mean(a, axis=None, dtype=None, out=None, keepdims=False):
    try:
        return np.mean(a, axis, dtype, out, keepdims)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def std(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    try:
        return np.std(a, axis, dtype, out, ddof, keepdims)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def min(a, axis=None, out=None, keepdims=False, initial=None, where=True):
    try:
        return np.min(a, axis, out, keepdims, initial, where)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def max(a, axis=None, out=None, keepdims=False, initial=None, where=True):
    try:
        return np.max(a, axis, out, keepdims, initial, where)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def sin(x, out=None):
    try:
        return np.sin(x, out)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def cos(x, out=None):
    try:
        return np.cos(x, out)

    except Exception as e:
        print("An error occurred:", str(e))
        raise
def tan(x, out=None):
    try:
        return np.tan(x, out)

    except Exception as e:
        print("An error occurred:", str(e))
        raise