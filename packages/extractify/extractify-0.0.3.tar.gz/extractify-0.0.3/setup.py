from setuptools import setup, find_packages
import os

# Read the content of README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as f:
    readme = f.read()

setup(
    name="extractify",
    version="0.0.3",
    packages=find_packages(),
    install_requires=[
        "tika",
        "openpyxl",
        "argparse",
        "tqdm",
        "boto3"
    ],
    entry_points={
        "console_scripts": [
            "extractify = extractify.main:main"
        ]
    },
    long_description=readme,
    long_description_content_type="text/markdown",
)