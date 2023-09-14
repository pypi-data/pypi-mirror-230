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
import numpy as np
import pandas as pd
from datamason.visualization import visualize
import seaborn as sns
import warnings

import matplotlib
matplotlib.use('Agg')  # Set backend

class TestFunctions(unittest.TestCase):

    def test_plot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                x = [1, 2, 3]
                y = [4, 5, 6]
                visualize.plot(x, y)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_scatter(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                x = np.random.rand(10)
                y = np.random.rand(10)
                visualize.scatter(x, y)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_bar(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                x = ['A', 'B', 'C']
                y = [4, 5, 6]
                visualize.bar(x, y)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_hist(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = np.random.randn(100)
                visualize.hist(data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_boxplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = pd.DataFrame({'A': np.random.randn(100), 'B': np.random.randn(100)})
                visualize.boxplot(data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_pie(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                x = [45, 30, 25]
                visualize.pie(x)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_displot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = np.random.randn(100)
                visualize.displot(data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_heatmap(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('flights').pivot(index='month', columns='year', values='passengers')
                visualize.heatmap(data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_pairplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('iris')
                visualize.pairplot(data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_violinplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.violinplot(x='day', y='total_bill', data=data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_joinplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.joinplot(data=data, x='total_bill', y='tip')
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_countplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.countplot(x='day', data=data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_lmplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.lmplot(data=data, x='total_bill', y='tip')
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_regplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.regplot(data=data, x='total_bill', y='tip')
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_kdeplot(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.kdeplot(data=data, x='total_bill')
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_facetgrid(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('tips')
                visualize.facetgrid(data=data, col='time', row='sex')
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")

    def test_clustermap(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                data = sns.load_dataset('flights').pivot(index='month', columns='year', values='passengers')
                visualize.clustermap(data)
            except Exception as e:
                self.fail(f"An unexpected error occurred: {str(e)}")