from setuptools import find_packages, setup

# setup requires requirements.txt:
setup_requirements = ['setuptools>=42', 'wheel']
test_requirements = ['pytest>=6', 'pytest-cov']
install_requires = ['geopandas >= 0.13.2',
                    'ingester3 == 1.9.1',
                    'joblib == 1.3.2',
                    'lightgbm == 4.0.0',
                    'matplotlib >= 3.7.0',
                    'mlflow >= 2.6.0',
                    'numpy == 1.25.0',
                    'pandas == 1.5.2',
                    'seaborn == 0.12.2',
                    'scikit-learn >= 1.3.0',
                    'sqlalchemy == 1.4.49',
                    'views-mapper2',
                    'xgboost == 1.7.6',
                    'viewser == 6.0.0',
                    'tqdm == 4.66.1',
                    'seaborn == 0.12.2']

setup(
    author="Tom Daniel Grande",
    author_email="tomdgrande@gmail.com",
    name="stepshifter3",
    version="0.0.1",
    description="A general purpose stepshifting algorithm for tabular data, based on BaseEstimator.",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    setup_requires=setup_requirements,
    test_suite='tests',
    license='MIT',
    url="https://www.github.com/prio-data/stepshifter3",
    tests_require=test_requirements,
    install_requires=install_requires
)
