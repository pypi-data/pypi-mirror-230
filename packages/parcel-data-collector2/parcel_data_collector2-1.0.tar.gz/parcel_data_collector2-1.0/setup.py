from setuptools import setup, find_packages

# Now, read the file again in your setup.py
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="parcel_data_collector2",
    version="1.0",
    packages=find_packages(),
    license="MIT",
    install_requires=requirements,
)
