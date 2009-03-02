from setuptools import setup

setup(name='Blogofile',
      version='0.1',
      description='A blog engine/compiler, inspired by Jekyll.',
      author='Ryan McGuire',
      author_email='ryan@enigmacurry.com',
      url='http://www.blogofile.com',
      license='Public Domain',
      packages=['blogofile'],
      include_package_data = True,
      install_requires =['mako',
                         'BeautifulSoup',
                         'pytz',
                         'pyyaml',
                         'textile'],
      entry_points="""
      [console_scripts]
      blogofile = blogofile:main
      """,
      )
