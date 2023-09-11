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
    version="0.1.8",
    packages=find_packages(),
    install_requires=install_requires,
    package_data={
        "torch_build_nn": ["torch_build_nn/distributed/optim/*"],
        # "torch_build_nn": ["torch_build_nn/functional_optim.csv"],
    },
)
