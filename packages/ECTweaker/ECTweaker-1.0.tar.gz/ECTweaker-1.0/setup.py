import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ECTweaker",                       # This is the name of the package
    version="1.0",                          # The initial release version
    author="Aditya Kumar Bajpai (YoCodingMonster)",                     # Full name of the author
    description="ECTweaker Library for python allows users to read/write and control the EC of laptops, specially MSI!",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
    ],                                      # Information to filter the project on PyPi website
    py_modules=["ECTweaker"],               # Name of the python package
    package_dir={'':'ECTweaker/src'},       # Directory of the source code of the package
    install_requires=[]                     # Install other dependencies if any
)
