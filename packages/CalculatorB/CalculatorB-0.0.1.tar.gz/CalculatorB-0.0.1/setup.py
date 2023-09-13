from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Simple Calculator'


# Setting up
setup(
    name="CalculatorB",
    version=VERSION,
    author="Kestutis Gricius",
    author_email="gricius.k@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'Calculator', 'CalculatorB'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
