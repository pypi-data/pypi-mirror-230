from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = [] 

setup(
    name="nlp_metrics",
    version="0.2.0",
    author="Tao Xiang",
    author_email="tao.xiang@tum.de",
    description="A package of RL algorithms",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/leoxiang66/nlp_metrics",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
    ],
)