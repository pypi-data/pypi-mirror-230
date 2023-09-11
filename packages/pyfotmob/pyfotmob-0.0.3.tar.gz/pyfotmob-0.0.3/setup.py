import setuptools
import subprocess
import os

fotmob_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in fotmob_version:
    v,i,s = fotmob_version.split("-")
    fotmob_version = v + "+" + i + ".git." + s

assert "-" not in fotmob_version
assert "." in fotmob_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyfotmob",
    version=fotmob_version,
    author="Youssef Ermili",
    author_email="youssef.ermili@gmail.com",
    description="A Python library for interacting with the FotMob API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/Yoo-Joo/PyFotMob",
    packages=setuptools.find_packages(),
    package_data={"fotmob": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    install_requires=["requests==2.31.0", "pydantic==1.10.8", "python-benedict==0.32.0"],
)
