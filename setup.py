from setuptools import setup, find_packages, Extension

NAME = 'warsa'

VERSION = '0.1.0'

DESCRIPTION = 'WARSA - tools for water resources system analysis'

LONG_DESCRIPTION = 'WARSA - tools for water resources system analysis'

config = {
    'description': 'warsa',
    'author': 'Jackson Roehrig',
    'url': '',
    'download_url': '',
    'author_email': 'jackson.roehrig@th-koeln.de',
    'version': '0.1',
    'install_requires': ['numpy', 'pandas', 'netCDF4'],
    'packages': ['warsa'],
    'scripts': [],
    'name': 'warsa'
}

CLASSIFIERS = [  # https://pypi.python.org/pypi?:action=list_classifiers
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Cython',
    'Programming Language :: C++',
    'Topic :: Scientific/Engineering :: Hydrology and Water Resources Management'
]

module1 = Extension(name='washmor', sources=['washmor.cpp'])

setup(
    name=NAME,
    version=VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author='Jackson Roehrig',
    author_email='Jackson.Roehrig@th-koeln.de',
    maintainer='Jackson.Roehrig@th-koeln.de',
    license='MIT',
    url='http://warsa.de/warsa/',
    download_url='https://github.com/JRoehrig/warsa',
    packages=find_packages(),
    ext_modules=[module1],  # To trick build into running build_ext
    scripts=[]

)
