#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    with open(filename) as f:
        lineiter = [line.strip() for line in f]
    return [line for line in lineiter if line and not line.startswith("#")]


requirements = parse_requirements("requirements.txt")

test_requirements = parse_requirements("requirements_dev.txt")

setup(
    author="Javi Palanca",
    author_email='jpalanca@dsic.upv.es',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Internet :: XMPP',
    ],
    description="SPADE Normative Plugin",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='spade_norms',
    name='spade_norms',
    packages=find_packages(include=['spade_norms', 'spade_norms.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/javipalanca/spade_norms',
    version='0.1.2',
    zip_safe=False,
)
