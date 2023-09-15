from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hql_parser',
    version='0.0.7',
    description='Parsing DDL files of HIVE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/hrosmendez/hql_parser',
    author='Henry Rosales',
    author_email='hrosmendez@gmail.com',

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.10',
    ],

    keywords='parser;sql;hive;ddl',
    packages=find_packages(exclude=['docs']),
    python_requires='>=3.4',
    install_requires=[''],
    package_data={},
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/hrosmendez/hql_parser',
        'Funding': 'https://gitlab.com/hrosmendez/hql_parser',
        'Say Thanks!': 'https://gitlab.com/hrosmendez/hql_parser',
        'Source': 'https://gitlab.com/hrosmendez/hql_parser',
    },
)
    
'''
-------------------------
   - python3 -m pip install --user --upgrade setuptools wheel
   - python3 setup.py sdist bdist_wheel
   - python3 -m pip install --user --upgrade twine
   - python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
      > Enter username and password
------------------------------
'''
 
