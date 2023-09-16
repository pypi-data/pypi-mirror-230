from setuptools import setup, find_packages

setup(
    name='conspira',
    version='0.1.5',
    author='Meng Xiao',
    description='This is a package for conspiratory theory content identification.',
    packages=find_packages(),
    install_requires=[
        'jieba',
        'scikit-learn',
        'requests',
    ],
    package_data={'conspira': ['resources/*']},
    
)