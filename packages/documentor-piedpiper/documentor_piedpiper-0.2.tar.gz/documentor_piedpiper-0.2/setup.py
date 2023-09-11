from setuptools import setup, find_packages

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name="documentor_piedpiper",
    version="0.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tree-sitter",
        "pygit2",
        "langchain",
        "openai",
        "wheel"
    ],
    entry_points={
        'console_scripts': [
            'documentor_run = src.main:main',
        ],
    },
)
