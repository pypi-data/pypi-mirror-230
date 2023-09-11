import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ezconfig-client",
    version="0.5",
    author="RiichTT",
    author_email="tolibo@hotmail.com",
    description="ezconfig client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riichg5/ezconfig_client",
    packages=setuptools.find_packages(),
    install_requires=['requests>=2.22.0', "retrying>=1.3.4"],
    entry_points={
        'console_scripts': [
            'ezconfig_client=ezconfig_client:main'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)