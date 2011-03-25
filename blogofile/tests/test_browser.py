# Selenium tests for the builtin Blogofile server. This is only
# intended to be run in a virtualenv via tox. Selenium isn't working
# for me in Python3 right now. Blogofile will be run using the
# virtualenv python but selenium will be run with the system python2.

import unittest
import tempfile
import shutil
import os
import subprocess
import shlex
import time
from selenium import webdriver

from . import selenium_helpers

class TestBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #Remember the current directory to preserve state
        cls.previous_cwd = os.getcwd()
        #Create a staging directory that we can build in
        cls.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(cls.build_path)
        #Initialize and build the site
        subprocess.Popen(shlex.split("blogofile init blog_unit_test")).wait()
        subprocess.Popen(shlex.split("blogofile build")).wait()
        #Start the server
        cls.port = 42042
        cls.url = "http://localhost:"+str(cls.port)
        cls.server = subprocess.Popen(shlex.split("blogofile serve {0}".
                                                   format(cls.port)))
        cls.chrome = webdriver.Chrome()
    @classmethod
    def tearDownClass(cls):
        cls.chrome.stop_client()
        #Stop the server
        cls.server.kill()
        #go back to the directory we used to be in
        os.chdir(cls.previous_cwd)
        #Clean up the build directory
        shutil.rmtree(cls.build_path)
        
    def testBuildAndServe(self):
        self.chrome.get(self.url)
        time.sleep(15)
