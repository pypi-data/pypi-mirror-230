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

import matplotlib.pyplot as plt
import seaborn as sns

def plot(x, y, render=True, **kwargs):

    try:
        # Original code
        plt.plot(x, y, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing plot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def scatter(x, y, render=True, **kwargs):

    try:
        # Original code
        plt.scatter(x, y, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing scatter: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def bar(x, height, render=True, **kwargs):

    try:
        # Original code
        plt.bar(x, height, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing bar: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def hist(x, render=True, **kwargs):

    try:
        # Original code
        plt.hist(x, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing hist: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def boxplot(x, render=True, **kwargs):

    try:
        # Original code
        plt.boxplot(x, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing boxplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def pie(x, render=True, **kwargs):

    try:
        # Original code
        plt.pie(x, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing pie: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def displot(a, render=True, **kwargs):

    try:
        # Original code
        sns.displot(a, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing displot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def heatmap(data, render=True, **kwargs):

    try:
        # Original code
        sns.heatmap(data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing heatmap: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def pairplot(data, render=True, **kwargs):

    try:
        # Original code
        sns.pairplot(data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing pairplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def violinplot(x, y, data, render=True, **kwargs):

    try:
        # Original code
        sns.violinplot(x=x, y=y, data=data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing violinplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def joinplot(x, y, data, render=True, **kwargs):

    try:
        # Original code
        sns.jointplot(x=x, y=y, data=data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing joinplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def countplot(x, data, render=True, **kwargs):

    try:
        # Original code
        sns.countplot(x=x, data=data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing countplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def lmplot(x, y, data, render=True, **kwargs):

    try:
        # Original code
        sns.lmplot(x=x, y=y, data=data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing lmplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def regplot(x, y, data, render=True, **kwargs):

    try:
        # Original code
        sns.regplot(x=x, y=y, data=data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing regplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def kdeplot(data, x, render=True, **kwargs):

    try:
        # Original code
        sns.kdeplot(data=data, x=x, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing kdeplot: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def facetgrid(data, col, row, render=True, **kwargs):

    try:
        # Original code
        sns.FacetGrid(data, col=col, row=row, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing facetgrid: {e}')
        plt.close()  # Close the figure to avoid memory leaks
def clustermap(data, render=True, **kwargs):

    try:
        # Original code
        sns.clustermap(data, **kwargs)
        plt.show()
    except Exception as e:
        print(f'An error occurred while executing clustermap: {e}')
        plt.close()  # Close the figure to avoid memory leaks