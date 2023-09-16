from setuptools import find_packages, setup

setup(
    name="funcyou",
    version="1.1.0",
    author="Tikendra sahu",
    author_email="tikendraksahu1029@gmail.com",
    description="useful functions to reuse and save time",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "scikit-learn",
        "pandas",
        "numpy",
        "kaggle",
        "seaborn",
    ],
)
