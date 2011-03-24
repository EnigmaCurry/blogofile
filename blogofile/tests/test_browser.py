import unittest
import tempfile
import shutil
import os
from selenium import webdriver

from .. import main
from .. import server
from . import selenium_helpers

class TestBrowser(unittest.TestCase):
    def setUp(self):
        main.do_debug()
        #Remember the current directory to preserve state
        self.previous_cwd = os.getcwd()
        #Create a staging directory that we can build in
        self.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(self.build_path)
        #Reinitialize the configuration
        main.config.init()
        #Build the unit test site
        main.main("init blog_unit_test")
        main.main("build")
        #Start the server
        self.port = 42042
        self.url = "http://localhost:"+str(self.port)
        self.server = server.Server(self.port)
        self.server.start()
        self.chrome = webdriver.Chrome()
        
    def tearDown(self):
        chrome.stop_client()
        #Revert the config overridden options
        main.config.override_options = {}
        #Stop the server
        self.server.shutdown()
        #go back to the directory we used to be in
        os.chdir(self.previous_cwd)
        #Clean up the build directory
        shutil.rmtree(self.build_path)
        
    def testBuildAndServe(self):
        chrome.get(self.url)
