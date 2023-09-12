import setuptools

PACKAGE_NAME = "location-local"
package_dir = "location_local_python"

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.28',  # https://pypi.org/project/location-local/
    author="Circles",
    author_email="info@circles.life",
    description="Location Locatal PyPI Package",
    long_description="This is a package for sharing common OpenCage function used in different repositories",
    long_description_content_type="text/markdown",
    url="https://github.com/javatechy/dokr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
