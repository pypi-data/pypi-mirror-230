from setuptools import setup, find_packages

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name="documentor-piedpiper",
    version="0.6",
    packages=find_packages(),
    install_requires=[
        "tree-sitter",
        "pygit2",
        "langchain",
        "openai",
        "wheel"
    ],
    entry_points={
        'console_scripts': [
            'documentor_run = __main__:main',
        ],
    }
)
