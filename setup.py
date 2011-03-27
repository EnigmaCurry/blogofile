from setuptools import setup, find_packages, Command
from setuptools.command.install import install as SetuptoolsInstaller
from distutils.command.sdist import sdist
import sys
import os
import os.path
import glob
import subprocess
import shutil

def setup_python2():
    #Blogofile is written for Python 3.
    #But we can also experimentally support Python 2 with lib3to2.
    from lib3to2 import main as three2two
    from distutils import dir_util
    import shutil
    import shlex
    tmp_src = "src_py2"
    try:
        shutil.rmtree(tmp_src)
    except OSError:
        pass #ignore if the directory doesn't exist.
    shutil.copytree("blogofile",os.path.join(tmp_src,"blogofile"))
    three2two.main("lib3to2.fixes",shlex.split("-w {0}".format(tmp_src)))
    return tmp_src

dependencies = ["mako",
                "markdown",
                "textile",
                "pytz",
                "pyyaml",
                "docutils"]
dependency_links = []

if sys.version_info < (3,):
    sys.path.insert(0,"src_py2")
    src_root = os.path.join("src_py2","blogofile")
    try:
        import blogofile
    except ImportError:
        print("-"*80)
        print("Python 3.x is required to develop and build Blogofile.")
        print("Python 2.x versions of Blogofile can be installed with "
              "a stable tarball\nfrom PyPI. e.g. 'easy_install blogofile'\n")
        print("Alternatively, you can build your own tarball with "
              "'python3 setup.py sdist'.")
        print("This will require Python 3 and 3to2, and will produce a tarball "
              "that can be\ninstalled in either Python 2 or 3.")
        print("-"*80)
        sys.exit(1)
else:
    dependencies.remove("markdown")
    dependencies.append("markdown>=2.0.3-py3k")
    dependencies.remove("textile")
    dependencies.append("textile>=2.1.4-py3k")
    dependency_links.append("http://github.com/EnigmaCurry/python-markdown-py3k/tarball/2.0.3#egg=markdown-2.0.3-py3k")
    dependency_links.append("http://github.com/EnigmaCurry/textile-py3k/tarball/2.1.4#egg=textile-2.1.4-py3k")
    src_root = "blogofile"
    import blogofile
    blogofile.zip_site_init()

class sdist_py2(sdist):
    "sdist for python2 which runs 3to2 over the source before packaging"
    def run(self):
        setup_python2()
        sdist.run(self)
        shutil.rmtree("src_py2")
        
class Test(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import tox
        tox.cmdline()

setup(name="Blogofile",
      version=blogofile.__version__,
      description="A static website compiler and blog engine",
      author="Ryan McGuire",
      author_email="ryan@enigmacurry.com",
      url="http://www.blogofile.com",
      license="MIT",
      packages=["blogofile", "blogofile.site_init"],
      package_dir = {"blogofile": src_root},
      package_data = {"blogofile.site_init": ["*.zip"]},
      install_requires = dependencies,
      dependency_links = dependency_links,
      cmdclass = {"test":Test,"sdist":sdist_py2},
      entry_points="""
      [console_scripts]
      blogofile = blogofile.main:main
      """
      )
