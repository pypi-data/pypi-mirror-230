from setuptools import setup, find_packages

setup(
    name='conspira',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'jieba',
        'scikit-learn',
    ],
    package_data={'conspira': ['resources/*']},
    
)