from setuptools import setup, find_packages

setup(
    name='ale-uy',
    version='1.1',
    description='herramienta para realizar limpieza, modelado y visualizacion de datos de manera sencilla y eficiente.',
    author='ale-uy',
    author_web='https://ale-uy.github.io/',
    url='https://github.com/ale-uy/DataScience',
    packages=find_packages(),
    install_requires=[
        'numpy==1.22.2',
        'pandas==1.4.2',
        'scikit-learn==1.0.2',
        'plotly==5.7.0',
        'matplotlib==3.5.1',
        'lightgbm==3.3.2',
        'xgboost==1.5.0',
        'catboost==0.27.0',
        'scipy==1.8.0',
    ],
)
