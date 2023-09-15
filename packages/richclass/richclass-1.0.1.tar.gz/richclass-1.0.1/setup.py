from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="richclass",
    version="1.0.1",
    description="A collection of feature rich classes",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UpAllNate/richclass",
    author="UpAllNate",
    author_email="upallnate@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords = ["class", "features", "tutorial"],
    extras_require={
        "dev": ["twine>=4.0.2"],
    },
)