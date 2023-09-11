from setuptools import setup, find_packages

install_requires = [
    "filelock",
    "typing-extensions",
    "sympy",
    "networkx",
    "jinja2",
    "fsspec",
]
setup(
    name="torch_build_nn",
    version="0.1.6",
    packages=find_packages(),
    install_requires=install_requires,
)
