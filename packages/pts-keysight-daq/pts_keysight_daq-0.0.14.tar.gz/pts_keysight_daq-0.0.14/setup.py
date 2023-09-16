from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pts_keysight_daq",
    version="0.0.14",
    author="Pass testing Solutions GmbH",
    description="Keysight DAQ 34980A Diagnostic Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="shuparna@pass-testing.de",
    url="https://gitlab.com/pass-testing-solutions/keysight34980a-interface",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    py_modules=["pts_keysight_daq"],
    install_requires=["pyvisa==1.12.0", "pyvisa-py==0.5.3"],
    packages=find_packages(include=['pts_keysight_daq']),
    include_package_data=True,
)
