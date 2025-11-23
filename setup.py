from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="LLMOPS-3/Study_Buddy",
    version="0.1",
    author="yousseftahoun",
    packages=find_packages(),
    install_requires = requirements,
)