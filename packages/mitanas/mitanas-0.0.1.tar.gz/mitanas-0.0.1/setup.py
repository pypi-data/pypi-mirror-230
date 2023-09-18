from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()
setup(
    name="mitanas",
    version="0.0.1",
    description="Make IT AN Autostart Script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anderson Araújo",
    author_email="andersondev.ssh@gmail.com",
    url="https://github.com/andersonssh/mitanas",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyinstaller"
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "black",
            "isort"
        ]
    },
    packages=["mitanas"]
)
