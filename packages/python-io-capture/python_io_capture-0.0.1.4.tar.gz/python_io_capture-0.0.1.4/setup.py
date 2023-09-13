from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

PROJECT_URLS = {
    "Bug Tracker": "https://github.com/SecurityLab-UCD/python-io-capture/issues",
    "Documentation": "https://github.com/SecurityLab-UCD/python-io-capture/blob/main/README.md",
    "Source Code": "https://github.com/SecurityLab-UCD/python-io-capture",
}

setup(
    name="python_io_capture",
    description="capture and report function IO at runtime",
    author="SecurityLab-UCD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls=PROJECT_URLS,
    author_email="yfhe@ucdavis.edu",
    version="0.0.1.4",
    packages=find_packages(),
    python_requires=">=3.8",
)
