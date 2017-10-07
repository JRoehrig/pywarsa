try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'warsa',
    'author': 'Jackson Roehrig',
    'url': '',
    'download_url': '',
    'author_email': 'Jackson.Roehrig@th-koeln.de',
    'version': '0.1',
    'install_requires': ['nose', 'numpy', 'pandas', 'netCDF4'],
    'packages': ['warsa'],
    'scripts': [],
    'name': 'warsa'
}

setup(**config)
