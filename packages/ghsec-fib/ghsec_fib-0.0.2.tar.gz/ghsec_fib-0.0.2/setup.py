from setuptools import find_packages, setup
import pathlib
with open(str(pathlib.Path(__file__).parent.absolute()) + "/version.py", "r") as fh:
     version = fh.read().split("=")[1].replace('"', "").lstrip()

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="ghsec_fib",
    version=version,
    author="ghsec",
    author_email="security@griphands.tech",
    description="Calculates a Fibonacci number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kohelet/ghsec_fib",
    install_requires=[
        "dill>=0.2.8"
        ],
    extras_require={
        'server': ["Flask>=1.0.0"]
    },
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    tests_require=["pytest"],
    entry_points={
        'console_scripts': [ 'fib-number=ghsec_fib_py.cmd.fib_numb:fib_numb',],
    },
)