import unittest
import tempfile
import shutil
import os
from .. import main

class TestBuild(unittest.TestCase):
    def setUp(self):
        #Remember the current directory to preserve state
        self.previous_dir = os.getcwd()
        #Create a staging directory that we can build in
        self.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(self.build_path)
    def tearDown(self):
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)
    def testBuildDefault(self):
        """Initialize and build the default site, just doing a cursory look to see if _site was built"""
        main.main("--init")
        main.main("--build")
        lsdir = os.listdir(os.path.join(self.build_path,"_site"))
        for fn in ("index.html","feed","category"):
            assert(fn in lsdir)
    
