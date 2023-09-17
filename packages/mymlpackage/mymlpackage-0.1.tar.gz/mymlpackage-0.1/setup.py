from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mymlpackage",
    version="0.1",
    author="Lina Beltrán",
    author_email="linam.beltran@udea.edu.co",
    description="A collection of minimal and clean implementations of machine learning algorithms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmbd92/ML_II_UdeA/tree/main/Taller2/mymlpackage",
    license="MIT",
    packages=["mymlpackage"],
    zip_safe=False,
)
