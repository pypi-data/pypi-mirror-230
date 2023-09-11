import setuptools

# Package metadata
NAME = 'OracUery'
VERSION = '1.0.2'
DESCRIPTION = 'Python module for generating SQL queries'
LONG_DESCRIPTION = """
Oracuery is a comprehensive Python module that simplifies database interaction by providing a set of powerful functions to generate SQL queries effortlessly. Whether you're working with databases in your web application, data analysis project, or any Python-based application, Oracuery streamlines the process, saving you time and reducing the complexity of writing SQL queries.
"""

# Author information
AUTHOR = 'BDakshP'
AUTHOR_EMAIL = 'bhalaladaksh613@gmail.com'

# License information
LICENSE = 'MIT'

# Package dependencies
INSTALL_REQUIRES = [
    'numpy>=1.0.0',  # Example: Require NumPy version 1.0.0 or higher
    'argparse',
]

# Additional dependencies for specific platforms
EXTRA_REQUIRES = {
    'macos': ['macos-specific-library>=1.0.0'],  # Add macOS specific libraries here
    'windows': ['windows-specific-library>=1.0.0'],  # Add Windows specific libraries here
    'linux': ['linux-specific-library>=1.0.0'],  # Add Linux specific libraries here
}

# Package classifiers
CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Topic :: Database',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
    'Intended Audience :: Developers',
    'Development Status :: 5 - Production/Stable',
]

# Package URLs
URL = 'https://github.com/DakshBhalala/Oracle-Query'

# Entry points (console scripts)
ENTRY_POINTS = {
    'console_scripts': [
        'oracuery-cli = oracuery.cli:main',
    ],
}

# Package distribution details
setuptools.setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    url=URL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    python_requires='>=3.6',
    entry_points=ENTRY_POINTS,
    include_package_data=True,
    package_data={
        'oracuery': ['*.sql'],  # Include SQL files in the 'oracuery' package
    },
    platforms=['any'],
    zip_safe=True,
    keywords='SQL database query database-utility database-tool SQL-generator',
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    project_urls={
        'Documentation': 'https://github.com/DakshBhalala/Oracle-Query/blob/main/docs/index.md',
        'Changelog': 'https://github.com/DakshBhalala/Oracle-Query/blob/main/CHANGELOG.md',
        'GitHub Repository': URL,
        'PyPI Page': f'https://pypi.org/project/{NAME}/',
    },
)
