from setuptools import setup, find_packages
import os
import glob
import blogofile
from blogofile.site_init import zip_site_init
            
zip_site_init()

setup(name='Blogofile',
      version=blogofile.__version__,
      description='A blog engine/compiler, inspired by Jekyll.',
      author='Ryan McGuire',
      author_email='ryan@enigmacurry.com',
      url='http://www.blogofile.com',
      license='MIT',
      packages=["blogofile", "blogofile/site_init"],
      package_data = {"blogofile/site_init": ["*.zip"]},
      install_requires =['mako',
                         'BeautifulSoup',
                         'pytz',
                         'pyyaml',
                         'textile',
                         'markdown',
                         'argparse',
                         'pygments',
                         'docutils'],
      entry_points="""
      [console_scripts]
      blogofile = blogofile.main:main
      """
      )
