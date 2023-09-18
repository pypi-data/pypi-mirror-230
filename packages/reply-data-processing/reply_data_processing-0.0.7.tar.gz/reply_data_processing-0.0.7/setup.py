import setuptools
from pathlib import Path


this_directory = Path(__file__).parent
with open((this_directory / "README.md"), "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="reply_data_processing",
    version="0.0.7",
    author="Marianna Diachuk",
    author_email="marianna.d@reply.io",
    description="Package for processing data in multiple formats for Reply AI services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reply-team/reply_ai_data_processing",
    project_urls={
        "Bug Tracker": "https://github.com/reply-team/reply_ai_data_processing",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
)
