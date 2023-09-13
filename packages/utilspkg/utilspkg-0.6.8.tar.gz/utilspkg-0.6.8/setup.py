
import os
import sys
from setuptools import setup, find_packages

os.chdir('/Users/croft/VScode/ptacorechallenge/utilsfolder')

if '--version' in sys.argv:
    version_index = sys.argv.index('--version') + 1
    version = sys.argv[version_index]
    sys.argv.remove('--version')
    sys.argv.remove(version)
else:
    version = input("Please enter the version number in 0.0.0 format: ")

if not version:
    print("Skipping utilspkg upload (not an error).")
    sys.exit(0)  # Exit with status code 0 which means success

setup(
    name='utilspkg',
    version=version, # takes the version variable from the command line
    packages=find_packages(include=['utilspkg']),
    install_requires=[ # install_requires are not used when compiling. they are referenced when pip installs this package to ensure they're also installed. so important but not critical for me.
        'airtable-python-wrapper>=0.15.3',
        'openai>=0.27.7',
        'protobuf>=4.24.1',
        'python-dotenv>=1.0.0',
        'pytz>=2023.3',
        'slack-sdk>=3.21.3',
        'tenacity>=8.2.2',
        'PyYAML',
        'google-cloud-logging'
    ]
)


