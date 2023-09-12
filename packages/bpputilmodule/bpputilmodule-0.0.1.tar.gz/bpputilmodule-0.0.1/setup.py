import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bpputilmodule", # Replace with your own username
    version="0.0.1",
    author="Jeevani",
    author_email="jkondepati@bluepenguin.com",
    description="BPP accounting API internal library to reduce redundant code",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/jkondepati/bpputils",
    packages=['bpputilmodule'],
    install_requires=["requests", "json"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)