# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.


from setuptools import find_packages, setup
with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()







setup(
    name="lorahub",
    version="0.0.7",
    license_files=["LICENSE"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="deep learning",
    license="MIT",
    author="Lorahub team",
    author_email="liuqian@sea.com",
    url="https://github.com/sail-sg/lorahub",
    package_dir={"": "src"},
    packages=find_packages(),
    entry_points={},
    python_requires=">=3.8.0",
    requires=[
        'transformers',
        'peft',
        'nevergrad',
        'torch',
        'tqdm',
        'pandas',
        'numpy',
        'datasets'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)



