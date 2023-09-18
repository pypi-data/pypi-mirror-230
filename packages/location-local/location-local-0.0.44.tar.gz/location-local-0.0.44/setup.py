import setuptools

PACKAGE_NAME = "location-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.44',  # https://pypi.org/project/location-local/
    author="Circles",
    author_email="info@circles.life",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    description="Location Locatal PyPI Package",
    long_description="This is a package for sharing common OpenCage function used in different repositories",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=["mysqlclient",
                    "mysql-connector>=2.2.9",
                    "pytest>=7.4.1",
                    "database-without-orm-local>=0.0.79",
                    "logger-local>=0.0.59",
                    "language-local>=0.0.4",
                    "python-dotenv>=1.0.0",
                    "logzio-python-handler>=4.1.0",
                    "opencage>=2.3.0"]
)
