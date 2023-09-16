from setuptools import find_packages, setup

setup(
    name="eai-commons",
    packages=find_packages(exclude=["eai_commons_tests"]),
    version='0.0.4dev',
    install_requires=[
        "pydantic>=1.10.11",
        "coloredlogs>=15.0.1",
        "pytz>=2023.3",
        "pycryptodome>=3.18.0",
        "PyJWT>=2.6.0",
        "tqdm>=4.65.0",
    ],
)
