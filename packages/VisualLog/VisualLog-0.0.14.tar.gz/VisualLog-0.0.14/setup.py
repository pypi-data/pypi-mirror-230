import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="VisualLog",
    version="0.0.14",
    author="zengjf",
    author_email="zengjf42@163.com",
    description="Visual Log",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZengjfOS/VisualLog",
    project_urls={
        "Bug Tracker": "https://github.com/ZengjfOS/VisualLog/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.0",
    install_requires=[
        'matplotlib',
        'numpy',
    ],
)
