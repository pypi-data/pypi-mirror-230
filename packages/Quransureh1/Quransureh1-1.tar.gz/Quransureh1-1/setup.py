from setuptools import setup, find_packages

VERSION = '1'
DESCRIPTION = 'Quransureh1'
LONG_DESCRIPTION = 'First Python Package'

# Setting up
setup(
    name="Quransureh1",
    version=VERSION,
    author="Masoud Shafiei",
    author_email="masoudshafiei89@yahoo.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['quran', 'sureh1'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)