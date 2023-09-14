from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul-db-utils',
    version='3.0.0',
    description='Python ul db utils',
    author='Unic-lab',
    author_email='',
    url='https://gitlab.neroelectronics.by/unic-lab/libraries/common-python-utils/db-utils.git',
    packages=find_packages(include=['ul_db_utils*']),
    platforms='any',
    package_data={
        '': ['*.sql'],
        'ul_db_utils': ['py.typed'],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'uldbutls=ul_db_utils.main:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        "flask==2.1.3",  # FOR COMPATIBILITY
        "py-dateutil==2.2",

        "psycopg2-binary==2.9.5",
        "flask-sqlalchemy==2.5.1",
        "flask-migrate==3.1.0",
        "sqlalchemy[mypy]==1.4.41",
        "sqlalchemy-stubs==0.4",
        "sqlalchemy-utils==0.38.3",
        "sqlalchemy-serializer==1.4.1",
        "alembic==1.8.1",
        "mysql-connector-python==8.0.31",

        "redis==4.3.4",

        "types-psycopg2==2.9.18",
        "sqlalchemy-stubs==0.4",
        "types-flask-sqlalchemy==2.5.3",
        "types-sqlalchemy-utils==1.0.1",
        "types-sqlalchemy==1.4.40",
        "types-redis==4.3.13",
        "types-jinja2==2.11.9",
        "types-python-dateutil==2.8.19",
        # "types-requests==2.28.8",

        "ul-py-tool==1.15.42",
    ],
)
