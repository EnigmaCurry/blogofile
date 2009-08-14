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
        """Test to make sure blogs hosted in subdirectories off the root work"""
        main.main("--init")
        main.config.blog_url = "http://www.test.com/path/to/blog"
        main.main("--build")
        lsdir = os.listdir(os.path.join(self.build_path,"_site","path","to","blog"))
        for fn in ("category","page","feed"):
            assert(fn in lsdir)
    def testPermaPages(self):
        """Test that permapages are written"""
        main.main("--init")
        main.config.blog_url = "http://www.test.com/path/to/blog"
        main.main("--build")
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","2009","07","23","post-one"))
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","2009","07","23","post-two"))
    def testCategoryPages(self):
        """Test that permapages are written"""
        main.main("--init")
        main.config.blog_url = "http://www.test.com/path/to/blog"
        main.main("--build")
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","category","category-1","1"))
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","category","category-1"))
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","category","category-2"))
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","category","category-2","1"))
    def testFeeds(self):
        """Test that RSS/Atom feeds are written"""
        main.main("--init")
        main.config.blog_url = "http://www.test.com/path/to/blog"
        main.main("--build")
        #Whole blog feeds
        assert "index.xml" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","feed"))
        assert "index.xml" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","feed","atom"))
        #Per category feeds
        assert "index.xml" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","category","category-1","feed"))
        assert "index.xml" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","category","category-1","feed","atom"))
        
