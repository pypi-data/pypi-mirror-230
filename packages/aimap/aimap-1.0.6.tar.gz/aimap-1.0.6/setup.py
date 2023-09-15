# try using distribute or setuptools or distutils.
try:
    import distribute_setup
    distribute_setup.use_setuptools()
except ImportError:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
import re

# parse version from package/module without importing or evaluating the code
with open('aimap/__init__.py') as fh:
    for line in fh:
        m = re.search(r"^__version__ = '(?P<version>[^']+)'$", line)
        if m:
            version = m.group('version')
            break

if sys.version_info <= (3, 0):
    sys.stderr.write("ERROR: aimap requires Python 3 " +
                     "or above...exiting.\n")
    sys.exit(1)

setup(
    name="aimap",
    version=version,
    author="Sai Wang",
    author_email="skyws@outlook.com",
    description=''.join(["aimap provides a package and script for " +
                         "finding the modification from Adenosine to inosine (A to I)."]),
    license="MIT",
    keywords="sequence analysis",
    platforms="Posix; MacOS X",
    url="https://github.com/castualwang/aimap",  # project home page
    download_url="https://github.com/castualwang/aimap/releases",
    scripts=[os.path.join('bin', 'Adenosine_to_inosine.py')],
    packages=['aimap'],
    package_data={'aimap': ['test_result/*.txt']},
    include_package_date=True,
    install_requires=['biopython',
                      'pandas',
                      'gffutils'],
    python_requires='>=3',                  
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
    )
