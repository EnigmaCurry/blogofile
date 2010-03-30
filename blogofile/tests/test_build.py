import unittest
import tempfile
import shutil
import glob
import os
import re
from .. import main
from .. import util
import logging

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
        """Test to make sure blogs hosted in subdirectories
        off the webroot work"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com/~username",
            "blog_path":"/path/to/blog" }
        main.main("build")
        lsdir = os.listdir(os.path.join(self.build_path,"_site","~username",
                                        "path","to","blog"))
        for fn in ("category","page","feed"):
            assert(fn in lsdir)
    def testPermaPages(self):
        """Test that permapages are written"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com/",
            "blog_path":"/blog" }
        main.main("build")
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","blog",
                         "2009","07","23","post-1"))
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","blog",
                         "2009","07","24","post-2"))
    def testNoPosts(self):
        """Test when there are no posts, site still builds cleanly"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com/",
            "blog_path":"/blog" }
        shutil.rmtree("_posts")
        util.mkdir("_posts")
        main.main("build")
    def testPostInSubdir(self):
        "Test a post in a subdirectory of _posts"
        pass
    def testNoPostsDir(self):
        """Test when there is no _posts dir, site still builds cleanly"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com/",
            "blog_path":"/blog" }
        shutil.rmtree("_posts")
        logger = logging.getLogger("blogofile")
        #We don't need to see the error that this test checks for:
        logger.setLevel(logging.CRITICAL) 
        main.main("build")
        logger.setLevel(logging.ERROR)
    def testCategoryPages(self):
        """Test that categories are written"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/path/to/blog" }
        main.main("build")
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
    def testArchivePages(self):
        """Test that archives are written"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/path/to/blog" }
        main.main("build")
        assert "index.html" in os.listdir(
            os.path.join(self.build_path,"_site","path",
                         "to","blog","archive","2009","07","1"))
    def testFeeds(self):
        """Test that RSS/Atom feeds are written"""
        main.main("init blog_unit_test")
        main.config.override_options = {
            "site_url":"http://www.test.com",
            "blog_path":"/path/to/blog" }
        main.main("build")
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
    
    def testFileIgnorePatterns(self):
        main.main("init blog_unit_test")
        #Initialize the config manually
        main.config.init("_config.py")
        #Add some file_ignore_patterns:
        open("test.txt","w").close()
        open("test.py","w").close()
        #File ignore patterns can be strings
        main.config.file_ignore_patterns.append(r".*test\.txt$")
        #Or, they can be precompiled regexes
        p = re.compile(".*\.py$")
        main.config.file_ignore_patterns.append(p)
        main.config.recompile()
        main.do_build([], load_config=False)
        assert not "test.txt" in os.listdir(
            os.path.join(self.build_path,"_site"))
        assert not "test.py" in os.listdir(
            os.path.join(self.build_path,"_site"))
        
