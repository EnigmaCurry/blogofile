from setuptools import setup
import blogofile

setup(name='Blogofile',
      version=blogofile.__version__,
      description='A blog engine/compiler, inspired by Jekyll.',
      author='Ryan McGuire',
      author_email='ryan@enigmacurry.com',
      url='http://www.blogofile.com',
      license='Public Domain',
      packages=['blogofile', 'blogofile.site_init'],
      include_package_data = True,
      install_requires =['mako',
                         'BeautifulSoup',
                         'pytz',
                         'pyyaml',
                         'textile',
                         'markdown<2.0',
                         'argparse',
                         'pygments',
                         'docutils'],
      entry_points="""
      [console_scripts]
      blogofile = blogofile.main:main
      """,
      )
