import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pu4c",
    version="0.0.1",
    author="city945",
    author_email="city945@njust.edu.cn",
    description="A python utils package for city945",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/city945",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)