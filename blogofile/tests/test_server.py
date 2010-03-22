import unittest
import tempfile
import shutil
import os
import BeautifulSoup
from .. import main
from .. import server

class TestServer(unittest.TestCase):
    def setUp(self):
        main.do_debug()
        #Remember the current directory to preserve state
        self.previous_dir = os.getcwd()
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
        self.server = server.Server(42042)
        self.server.start()
    def tearDown(self):
        #Stop the server
        self.server.shutdown()
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)
    def testBuildAndServe(self):
        "test build server"
        pass
