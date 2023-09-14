## Release Status

**Current Release:** Beta (v0.7.1b1)

Welcome to DataMason! Our package is currently in the Beta release phase, showcasing a stable core functionality. While the primary features are rigorously tested and reliable, we are actively fine-tuning and evaluating additional features. Your insights and contributions are highly valued as we work towards a polished final release.

## Update Notes

**Latest Update:** Polyglot installation module added! Call it using _dm.install_polyglot()_

While the dependencies should be automatically installed when installing DataMason, if for some reason they are not found at import of the DataMason package, it will attempt to install them.

## Upcoming Enhancements

**Anticipated in v0.8.0b1 and Beyond:** Streamlined Package Structure

We are excited to share our vision for the future! In the upcoming version 0.8.0b1, and subsequent releases, we plan to introduce a restructured package. This enhancement is designed to simplify your experience by allowing direct access to core functionalities upon importing the package. You'll no longer need to specify individual modules during import or function calls, making DataMason even more intuitive and user-friendly.

Thank you for being a part of the DataMason journey. Your engagement and support drive our commitment to excellence in data science and analysis tools.

Stay tuned for further updates and feel free to contribute your expertise to our growing community!

# DataMason (v. 0.7.1b1)

DataMason is a comprehensive Python package designed to make data analysis and manipulation easier for data professionals of all skill levels. It offers a collection of tools to clean, transform, analyze, and visualize datasets, allowing users to uncover insights and make informed decisions.

## Features

- **Data Cleaning**: Easily identify and address data quality issues.
- **Data Transformation**: Reshape and transform datasets to fit your analysis needs.
- **Data Analysis**: Perform insightful data analysis to uncover patterns and trends.
- **Data Visualization**: Create meaningful visualizations that help communicate findings.
- **Machine Learning**: Utilize machine learning algorithms for predictive modeling.

## Installation

Install DataMason using pip:

```bash
pip install datamason
```

## Importing the Package and Subpackages

### Main Package

```python
import datamason as dm
```

### Subpackages

- **Analysis**: `import datamason.analysis as dm_analysis`
- **Clustering**: `import datamason.clustering as dm_clustering`
- **Data I/O**: `import datamason.data_io as dm_data_io`
- **Image Processing**: `import datamason.image_processing as dm_image_processing`
- **Integration**: `import datamason.integrate as dm_integrate`
- **Interpolation**: `import datamason.interpolate as dm_interpolate`
- **Linear Algebra**: `import datamason.linear_algebra as dm_linear_algebra`
- **Metrics**: `import datamason.metrics as dm_metrics`
- **Modeling**: `import datamason.modeling as dm_modeling`
- **Numerics**: `import datamason.numerics as dm_numerics`
- **Optimization**: `import datamason.optimize as dm_optimize`
- **Preparation**: `import datamason.prepare as dm_prepare`
- **Preprocessing**: `import datamason.preprocessing as dm_preprocessing`
- **Statistics**: `import datamason.statistics as dm_statistics`
- **Text Analysis**: `import datamason.text_analysis as dm_text_analysis`
- **Transformation**: `import datamason.transform as dm_transform`
- **Validation**: `import datamason.validation as dm_validation`
- **Visualization**: `import datamason.visualization as dm_visualization`

These are just examples, and not recommended best practices, for importing the subpackages.


## Testing (Currently Stable)

DataMason includes a comprehensive testing submodule that allows users to validate the functionality of the package. You can run the entire test suite by executing:

```python
import datamason as dm
dm.test()
```

This will provide a summary of the test results, including details of any failed tests.

## Example Usage

### data_io Subpackage

Functions related to data input and output.

#### io.py

- **read_csv()**: Example usage: `df = dm.data_io.read_csv('data.csv')`
- **to_csv()**: Example usage: `dm.data_io.to_csv(df, 'output.csv')`
- **read_excel()**: Example usage: `df = dm.data_io.read_excel('data.xlsx')`

### numerics Subpackage

Functions related to numerical operations.

#### numerical.py

- **array()**: Example usage: `arr = dm.numerics.array([1, 2, 3])`
- **linspace()**: Example usage: `arr = dm.numerics.linspace(0, 1, 10)`
- **arange()**: Example usage: `arr = dm.numerics.arange(0, 10, 2)`
- **reshape()**: Example usage: `reshaped_arr = dm.numerics.reshape(arr, (2, 5))`
- **dot()**: Example usage: `result = dm.numerics.dot(arr1, arr2)`
- **concatenate()**: Example usage: `concated = dm.numerics.concatenate((arr1, arr2))`
- **mean()**: Example usage: `mean_val = dm.numerics.mean(arr)`
- **std()**: Example usage: `std_val = dm.numerics.std(arr)`
- **min()**: Example usage: `min_val = dm.numerics.min(arr)`
- **max()**: Example usage: `max_val = dm.numerics.max(arr)`
- **np.sin()**: Example usage: `sine_values = dm.numerics.np.sin(arr)`
- **np.cos()**: Example usage: `cosine_values = dm.numerics.np.cos(arr)`
- **np.tan()**: Example usage: `tan_values = dm.numerics.np.tan(arr)`

### preprocessing Subpackage

Functions related to data preprocessing.

#### prepare.py

- **fillna()**: Example usage: `filled_df = dm.preprocessing.fillna(df, value=0)`
- **drop_duplicates()**: Example usage: `unique_df = dm.preprocessing.drop_duplicates(df)`
- **merge()**: Example usage: `merged_df = dm.preprocessing.merge(df1, df2, on='key')`
- **groupby()**: Example usage: `grouped = dm.preprocessing.groupby(df, 'column')`
- **pivot_table()**: Example usage: `pivoted = dm.preprocessing.pivot_table(df, values='value', index='index')`
- **cut()**: Example usage: `bins = dm.preprocessing.cut(df['column'], bins=3)`
- **get_dummies()**: Example usage: `dummies = dm.preprocessing.get_dummies(df['column'])`

#### transform.py

- **fillna()**: Example usage: `filled_df = dm.preprocessing.fillna(df, value=0)`
- **drop_duplicates()**: Example usage: `unique_df = dm.preprocessing.drop_duplicates(df)`
- **merge()**: Example usage: `merged_df = dm.preprocessing.merge(df1, df2, on='key')`
- **groupby()**: Example usage: `grouped = dm.preprocessing.groupby(df, 'column')`
- **pivot_table()**: Example usage: `pivoted = dm.preprocessing.pivot_table(df, values='value', index='index')`
- **cut()**: Example usage: `bins = dm.preprocessing.cut(df['column'], bins=3)`
- **get_dummies()**: Example usage: `dummies = dm.preprocessing.get_dummies(df['column'])`

### analysis Subpackage

Functions related to data analysis.

#### analysis.py

- **summarize()**: Example usage: `summary = dm.analysis.summarize(df)`
- **find_correlations()**: Example usage: `correlations = dm.analysis.find_correlations(df)`
- **count_values()**: Example usage: `value_counts = dm.analysis.count_values(df['column'])`

### visualization Subpackage

Functions related to data visualization.

#### visualize.py

- **plot()**: Example usage: `dm.visualization.plot(x, y)`
- **scatter()**: Example usage: `dm.visualization.scatter(x, y)`
- **bar()**: Example usage: `dm.visualization.bar(categories, values)`
- **hist()**: Example usage: `dm.visualization.hist(data, bins=10)`
- **boxplot()**: Example usage: `dm.visualization.boxplot(data)`
- **pie()**: Example usage: `dm.visualization.pie(sizes, labels=labels)`
- **show()**: Example usage: `dm.visualization.show()`
- **distplot()**: Example usage: `dm.visualization.distplot(data)`
- **heatmap()**: Example usage: `dm.visualization.heatmap(matrix)`
- **pairplot()**: Example usage: `dm.visualization.pairplot(df)`
- **violinplot()**: Example usage: `dm.visualization.violinplot(data)`
- **joinplot()**: Example usage: `dm.visualization.joinplot(x, y, data=df)`
- **countplot()**: Example usage: `dm.visualization.countplot(x='column', data=df)`
- **lmplot()**: Example usage: `dm.visualization.lmplot(x='x', y='y', data=df)`
- **regplot()**: Example usage: `dm.visualization.regplot(x='x', y='y', data=df)`
- **kdeplot()**: Example usage: `dm.visualization.kdeplot(data)`
- **facetgrid()**: Example usage: `grid = dm.visualization.facetgrid(df, col='column')`
- **clustermap()**: Example usage: `dm.visualization.clustermap(data)`


## Contributing

We welcome contributions from the community to help improve DataMason. If you're interested in contributing, please follow these steps:

1. **Share Your Ideas**: Before making significant changes, send an email with your thoughts and recommendations to the contact below. We'll discuss your ideas and how they fit into the project.

2. **Fork the Repository**: If your idea is approved, you can fork the repository and work on your changes.

3. **Submit a Pull Request**: Once you've made your changes, submit a pull request for review. Please ensure that your code adheres to the existing coding standards and includes appropriate tests and documentation.

4. **Review and Merge**: We'll review your pull request and provide feedback if necessary. Upon approval, your contribution will be merged into the project.

5. **Acknowledgment**: Contributors are valued members of our community, and we'll acknowledge your hard work in our project documentation.

For any questions or further guidance, please contact us at thyripian@gmail.com](mailto:thyripian@gmail.com).

Thank you for considering contributing to DataMason!


## License

MIT License

## Contact

thyripian@gmail.com
