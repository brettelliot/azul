import setuptools
import os


with open('README.rst', 'r') as fh:
    long_description = fh.read()

version_file = open(os.path.join('./', 'VERSION'))
version = version_file.read().strip()


setuptools.setup(
    name='azul',
    version=version,
    author='Brett Elliot',
    author_email='brett@theelliots.net',
    description="A command line tool and python package for downloading historical price data as CSV's ready for use in a zipline bundle.",
    long_description=long_description,
    url='https://github.com/brettelliot/azul',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=7.0',
        'Logbook>=1.4.1',
        'class-registry>=2.1.2',
        'numpy>=1.15.4',
        'pandas>=0.22.0',
        'zipline>=1.3.0',
        'bcolz<1,>=0.12.1',
        'bottleneck>=1.2.1',
        'scipy>=1.2.0'
    ],
    entry_points='''
        [console_scripts]
        azul=azul.scripts.azul:cli
    ''',
    license='MIT',
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)