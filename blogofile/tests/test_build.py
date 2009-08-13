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
        #Reinitialize the configuration
        main.config.init()
    def tearDown(self):
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)
    def testBlogSubDir(self):
        """Test to make sure blogs hosted in subdirectorys off the root work"""
        main.main("--init")
        main.config.blog_url = "http://www.test.com/path/to/blog"
        main.main("--build")
        lsdir = os.listdir(os.path.join(self.build_path,"_site","path","to","blog"))
        print "LSDIR: ",lsdir
        for fn in ("category","page","feed"):
            assert(fn in lsdir)
        
