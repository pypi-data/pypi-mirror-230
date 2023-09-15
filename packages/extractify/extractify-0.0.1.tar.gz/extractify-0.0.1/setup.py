from setuptools import setup, find_packages

setup(
    name="extractify",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "tika",
        "openpyxl",
        "argparse"
    ],
    entry_points={
        "console_scripts": [
            "extractify = extractify.main:main"
        ]
    },
)