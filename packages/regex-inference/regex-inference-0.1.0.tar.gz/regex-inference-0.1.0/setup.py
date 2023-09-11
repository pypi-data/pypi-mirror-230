"""
How to sent this package onto PyPi?

1) Building Package Release Tar:
```python setup.py sdist```

2) Upload Package to PyPi:
```pip install twine```
```twine upload dist/*```
"""
import pathlib
import setuptools
from setuptools import find_packages

with open("README.md", "r") as fh:

    long_description = fh.read()


with open(str(pathlib.Path(__file__).parent.absolute()) +
          "/regex_inference/version.py", "r") as fh:
    version = fh.read().split("=")[1].replace("'", "")

setuptools.setup(

    name="regex-inference",

    version=version,

    author="jeffreylin",

    author_email="jeffrey82221@gmail.com",

    description="Regex Inference Engine based on ChatGPT",

    long_description=long_description,

    long_description_content_type="text/markdown",

    url="https://github.com/jeffrey82221/regex_inference",

    packages=find_packages(exclude=('tests',)),

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",

    ],
    python_requires='>=3.8, !=3.11.*',
    tests_require=['pytest'],
    install_requires=[
        'openapi-schema-pydantic==1.2.4',
        'pydantic==1.10.12',
        'openai==0.27.8',
        'langchain==0.0.253',
        'random_regex'
    ]
)
