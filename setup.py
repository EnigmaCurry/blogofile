from setuptools import setup, find_packages
from setuptools.command.install import install as SetuptoolsInstaller
import sys
import os
import os.path
import glob

def setup_python2():
    #Blogofile is written for Python 3.
    #But we can also experimentally support Python 2 with lib3to2.
    from lib3to2 import main as three2two
    from distutils import dir_util
    import shutil
    import shlex
    tmp_root = os.path.join("build","py2_src")
    tmp_src = os.path.join(tmp_root,"blogofile")
    try:
        shutil.rmtree(tmp_src)
    except OSError:
        pass #ignore if the directory doesn't exist.
    shutil.copytree("blogofile",tmp_src)
    three2two.main("lib3to2.fixes",shlex.split("-w {0}".format(tmp_src)))
    return tmp_root

if sys.version_info <= (3,):
    src_root = setup_python2()
    sys.path.insert(0,src_root)
else:
    src_root = os.curdir

import blogofile
from blogofile.site_init import zip_site_init
            
zip_site_init()
        
setup(name="Blogofile",
      version=blogofile.__version__,
      description="A static website compiler and blog engine",
      author="Ryan McGuire",
      author_email="ryan@enigmacurry.com",
      url="http://www.blogofile.com",
      license="MIT",
      src_root=src_root,
      packages=["blogofile", "blogofile/site_init"],
      package_data = {"blogofile/site_init": ["*.zip"]},
      install_requires = ["mako",
                          "markdown>=2.0.3-py3k",
                          "textile>=2.1.4-py3k",
                          "pytz",
                          "pyyaml",
                          "docutils"],
      dependency_links = ["http://github.com/EnigmaCurry/python-markdown-py3k/tarball/2.0.3#egg=markdown-2.0.3-py3k",
                          "https://github.com/EnigmaCurry/textile-py3k/zipball/2.1.4#egg=textile-2.1.4-py3k"],
      entry_points="""
      [console_scripts]
      blogofile = blogofile.main:main
      """
      )
