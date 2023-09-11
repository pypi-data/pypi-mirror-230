try: from setuptools import setup, find_packages
except ImportError: from distutils.core import setup, find_packages

SETUP_CONF = \
dict (name = "watercycle",
      description = "Communications",
      download_url = "",

      license = "None",
      platforms = ['OS-independent', 'Many'],

      include_package_data = True,

      keywords = [],

      classifiers = [])

SETUP_CONF['version'] = '0.0.1'
SETUP_CONF['url'] = ''

SETUP_CONF['author'] = ''
SETUP_CONF['author_email'] = ''

SETUP_CONF['long_description'] = ''
SETUP_CONF['packages'] = find_packages()

setup(**SETUP_CONF)
