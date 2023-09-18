from time import time
import setuptools

# python -m build
# python -m twine upload dist/* --skip-existing

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uipy",
    version="1.0.3",
    author="jerry",
    author_email="6018421@qq.com",
    description="A UI library based on PySide 6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "uipy"},
    packages=setuptools.find_packages(where="uipy"),
    python_requires=">=3.8",
)
