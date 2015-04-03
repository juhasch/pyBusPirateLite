import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyBusPirateLite",
    version = "0.1",
    author = "Juergen Hasch",
    author_email = "juergen.hasch@elbonia.de",
    description = ("Python library for BusPirate"),
    license = "BSD",
    keywords = "BusPirate",
    url = "http://dangerousprototypes.com/docs/Bus_Pirate_Scripting_in_Python",
    packages=['pyBusPirateLite'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
