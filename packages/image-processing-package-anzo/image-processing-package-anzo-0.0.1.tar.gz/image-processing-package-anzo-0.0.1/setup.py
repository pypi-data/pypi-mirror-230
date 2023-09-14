from setuptools import setup, find_packages

with open("README.md", "r") as f: 
    page_description = f.read()

with open("requirements.txt") as f: 
    requirements = f.read().splitlines()

setup(
    name="image-processing-package-anzo",
    version="0.0.1",
    author="Anderson Soares Martins", 
    author_email="asmartins@live.com", 
    description="Resize and Combine Images",
    long_description="page_description", 
    long_description_content_type="text/markdown", 
    url="https://github.com/andersonsoaresmartins/image-processing-package.git",
    packages=find_packages(),
    install_requires="requirements.txt",
    python_requires='>=3.8',
)
