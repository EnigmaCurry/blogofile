# -*- coding: utf-8 -*-
import sys
from setuptools import setup
import blogofile


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3
PY26 = py_version == (2, 6)
if PY3:
    if py_version < (3, 2):
        raise RuntimeError(
            'On Python 3, Blogofile requires Python 3.2 or later')
else:
    if py_version < (2, 6):
        raise RuntimeError(
            'On Python 2, Blogofile requires Python 2.6 or later')

with open('README.rst', 'rt') as readme:
    long_description = readme.read()
with open('CHANGES.txt', 'rt') as changes:
    long_description += '\n\n' + changes.read()
with open('requirements/production.txt', 'rt') as reqs:
    requirements = reqs.read()
install_requires = [line for line in requirements.split('\n')
                    if line and not line.startswith('#')]
# TODO: There has to be a better way...
dependency_links = []
if PY3:
    textile_index = [i for i, item in enumerate(install_requires)
                     if item.startswith('textile')][0]
    install_requires[textile_index] += '-py3k'
    dependency_links = [
        'http://github.com/EnigmaCurry/textile-py3k/tarball/2.1.4'
        '#egg=textile-2.1.4-py3k']
if PY26:
    install_requires.append('argparse')

classifiers = [
    'Programming Language :: Python :: {0}'.format(py_version)
    for py_version in ['2', '2.6', '2.7', '3', '3.2']]
classifiers.extend([
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: Implementation :: CPython',
    'Environment :: Console',
    'Natural Language :: English',
])

setup(
    name="Blogofile",
    version=blogofile.__version__,
    description="A static website compiler and blog engine",
    long_description=long_description,
    author=blogofile.__author__,
    author_email="blogofile-discuss@googlegroups.com",
    url="http://www.blogofile.com",
    license="MIT",
    classifiers=classifiers,
    packages=["blogofile"],
    install_requires=install_requires,
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points={
        'console_scripts': ['blogofile = blogofile.main:main']},
)
