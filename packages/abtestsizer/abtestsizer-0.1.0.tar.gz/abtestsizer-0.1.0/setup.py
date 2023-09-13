from setuptools import setup, find_packages

setup(
    name='abtestsizer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'statsmodels',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A Python package for AB test sample size calculation and analysis.',
    license='MIT',
)