from setuptools import setup, find_packages

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name="documentor_piedpiper",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "tree-sitter",
        "pygit2",
        "langchain",
        "openai",
        "wheel"
    ],
)
