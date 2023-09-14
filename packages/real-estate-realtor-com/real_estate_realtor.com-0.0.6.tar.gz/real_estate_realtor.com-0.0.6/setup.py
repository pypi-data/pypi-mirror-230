import setuptools
PACKAGE_NAME = "real_estate_realtor.com"
package_dir = PACKAGE_NAME.replace("-", "_")

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name=PACKAGE_NAME,  
    version='0.0.6',
    author="Circles",
    author_email="info@circles.life",
    description="PyPI Package for Real estate python package",
    long_description="This is a package for sharing common realtor function used in different repositories",
    long_description_content_type="text/markdown",
    url="https://github.com/circles-zone/real-estate-realtor.com-selenium-imp-local-python-package",

    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'mysqlclient',
        'importer-local>=0.0.33',
        'logger-local>=0.0.55',
        'storage-local>=0.1.6',
        'database-without-orm-local>=0.0.68',
        'location-local>=0.0.23',
        'entity-type-local>=0.0.12',
        'logzio-python-handler>=4.1.1',
        'opencage>=2.3.0',
        'selenium',
        'pandas',
        'sqlalchemy'
    ],
)
