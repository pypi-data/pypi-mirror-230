from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()


setup(
    name="randetect",
    version="0.0.1",
    packages=find_packages(),
    package_data={'randetect': ['models/logistic_regression_model.joblib']},
    install_requires=requirements,
    author="Seyma SARIGİL",
    author_email="seymasa@icloud.com",
    description="A text analysis tool that predicts whether a given string appears random or meaningful.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seymasa/randetect",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
