from setuptools import setup, find_packages

VERSION = "0.0.4"
DESCRIPTION = "Sunscreen Python Interop Package"
LONG_DESCRIPTION = "Sunscreen Python Interop Package"

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="sunscreen_py",
    version=VERSION,
    author="SmartFHE",
    author_email="hello@sunscreen.tch",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
    packages=find_packages(),
    keywords=["cryptography", "sunscreen", "fhe", "bfv", "web3"],
    install_requires=[
        'torch',
        'importlib_resources',
        'importlib_metadata',
        'typing',
    ],
)
