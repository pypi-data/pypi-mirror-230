from setuptools import setup, find_packages

setup(
    name='precision-lasso',
    version='0.1',
    packages=find_packages(),
    install_requires=['scipy', 'numpy'
                      ],
    author='Haohan Wang',
    author_email='haohanw@illinois.edu',
    description='An implementation of Precision Lasso, a statistical model that promotes sparse variable selection in '
                'the presence of correlated and linearly dependent variables. ',
    license='LICENSE.txt',
    keywords="regression, variable-selection",
    url='https://github.com/Liu-Hy/precision-lasso',
)
