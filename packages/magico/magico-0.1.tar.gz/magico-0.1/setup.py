import setuptools
import os
import json

about = {}
with open(f"{os.path.abspath(os.path.dirname(__file__))}/src/magico/__version__.py", "r") as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name=about["__name__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    license=about["__license__"],

    packages=["magico"],
    package_data={"": ["LICENSE"]},
    package_dir={"": "src"},
    python_requires=">=3.7",

    project_urls={
        "Source": "https://github.com/jackyko8/magico",
        "Documentation": "https://github.com/jackyko8/magico/blob/main/tutorials/MagicO.ipynb",
        "Bug Tracker": "https://github.com/jackyko8/magico/issues",
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
