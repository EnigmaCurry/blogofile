import unittest
import tempfile
import shutil
import os
import mechanize
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
        self.port = 42042
        self.url = "http://localhost:"+str(self.port)
        self.server = server.Server(self.port)
        self.server.start()

    def tearDown(self):
        #Revert the config overridden options
        main.config.override_options = {}
        #Stop the server
        self.server.shutdown()
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)

    def testBuildAndServe(self):
        br = mechanize.Browser()
        #Test the index page
        br.open(self.url)
        #Click the title
        br.follow_link(text_regex="Your Blog's Name")
        assert br.geturl().strip("/") == self.url
        #Go to the chronological page
        br.follow_link(text_regex="chronological blog page")
        assert br.geturl() == self.url + "/blog/"
        #Go to page 2
        br.follow_link(text_regex="Next Page")
        #Go to page 3
        br.follow_link(text_regex="Next Page")
        #Go back to page 2
        br.follow_link(text_regex="Previous Page")
        #Go back to page 1
        br.follow_link(text_regex="Previous Page")
        assert br.geturl() == self.url + "/blog/page/1/"
        #Go to a permalink page:
        br.open("/blog/2009/08/29/post-seven/")
        #Go to one it's categories:
        br.follow_link(text_regex="General Stuff")
        #Go to the next category page
        br.follow_link(text_regex="Next Page")
        #Come back to the 1st category page
        br.follow_link(text_regex="Previous Page")
        assert br.geturl() == self.url + "/blog/category/general-stuff/1/"
        #Go to a archive page:
        br.open("/blog/archive/2009/08/1/")
        #Go to the next page of this archive
        br.follow_link(text_regex="Next Page")
        #Come back to the 1st archive page
        br.follow_link(text_regex="Previous Page")
        assert br.geturl() == self.url + "/blog/archive/2009/08/1/"

    def testServeSubdirectory(self):
        #The site was already built in setUp
        #Rebuild the site with a new config:
        main.config.site_url = "http://www.yoursite.com/people/ryan"
        main.do_build({},load_config=False)
        br = mechanize.Browser()
