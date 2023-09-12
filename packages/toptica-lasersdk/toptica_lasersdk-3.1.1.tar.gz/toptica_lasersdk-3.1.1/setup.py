from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version from the VERSION file
with open(path.join(here, 'VERSION'), encoding='utf-8') as f:
    version = f.read().strip()

setup(
    name='toptica_lasersdk',
    version=version,

    description='TOPTICA Python Laser SDK',
    
    long_description=long_description,
    long_description_content_type='text/x-rst',

    author='TOPTICA Photonics AG',
    author_email='info@toptica.com',

    url='https://toptica.github.io/python-lasersdk/',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],

    keywords='toptica photonics laser sdk dlcpro ichrome cle mle',

    namespace_packages=['toptica'],
    packages=find_packages(exclude=['devices', 'doc', 'examples', 'tests']),

    entry_points={
        'console_scripts': [
            'lasersdk_gen=toptica.lasersdk.lasersdk_gen:main',
        ],
    },

    install_requires=['ifaddr', 'pyserial'],

    python_requires='>=3.6, <3.12',
)
