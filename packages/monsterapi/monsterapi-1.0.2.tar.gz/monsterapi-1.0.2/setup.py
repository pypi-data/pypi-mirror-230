from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="monsterapi",
    version="1.0.2",
    author="Ramachandra Vikas Chamarthi",
    author_email="vikas@qblocks.cloud",
    description="A Python client for Monster API v2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qblocks/monsterapiclient",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests",
        "requests_toolbelt",
        "pydantic"
    ],
    extras_require={
        'tests': [
            'pytest',
            'unittest.mock; python_version<"3.3"',  # For Python versions less than 3.3, where mock is not in the stdlib
        ]
    }
)
