import unittest
import tempfile
import shutil
import os
import BeautifulSoup
from .. import main

class TestServer(unittest.TestCase):
    def setUp(self):
        #Remember the current directory to preserve state
        self.previous_dir = os.getcwd()
        #Create a staging directory that we can build in
        self.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(self.build_path)
        #Reinitialize the configuration
        main.config.init()
    def tearDown(self):
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)
    def testBuildAndServe(self):
        main.main("init blog_unit_test")
        main.main("build")
        #TODO: start server and test it serves correct pages
