######################################################################
#### Instructions for creating a new Blogofile plugin:
#### 1) Set module_name to the name of your plugin using only alpha-numeric
####    characters and the underscore :

module_name = "blogofile_plugin_test"

#### 2) Rename the blogofile_plugin_example directory to this same name.
#### 3) Edit module_name/__init__.py and configure the __dist__ object.
#### 4) Create your plugin's controllers, filters, and other files in
####    module_name/site_src
#### 5) Run "python setup.py develop" to start testing your plugin.
####    (You may need to be root or run virtualenv)
#### 6) Run 'blogofile plugin list' and you should see your plugin listed.
####
#### The rest of this file is boilerplate, and you can probably leave as is.
######################################################################

from setuptools import setup, find_packages
import os
import imp

def find_package_data(module, path):
    """Find all data files to include in the package"""
    files = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(module,path)):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath,filename),module))
    return {module:files}

#Setup the application using meta information from
#the plugin's own __dist__ object:
plugin = imp.load_package(module_name,module_name)
setup(name=module_name,
      description=plugin.__dist__['pypi_description'],
      version=plugin.__version__,
      author=plugin.__dist__["author"],
      url=plugin.__dist__["url"],
      packages=[module_name],
      package_data = find_package_data(module_name,"site_src"),
      include_package_data = True,
      install_requires =['blogofile'],
      entry_points = {
        "blogofile.plugins":
            ["{module_name} = {module_name}".format(**locals())]
        }
      )
