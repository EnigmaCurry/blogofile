#!/usr/bin/env python

__author__ = "Seth de l'Isle"

#### Usage:
## You can generate a Blogger export file by logging into blogger,
## then going to Settings -> Basic -> Export Blog.  You will get a
## file to download with the current date in the name and a .xml
## extension.  Running blogger2blogofile.py in that directory, with
## the filename of the export file as the only argument will generate
## a _posts directory ready for use with Blogofile.


import sys
try:
    import feedparser
except ImportError:
    print >> sys.stderr, """This tool requires the universal feedparser module.

Depending on your tools, try:
    apt-get install python-feedparser
or: 
    easy_install feedparser

or check out the download files at http://code.google.com/p/feedparser/downloads/list
 """ 
    sys.exit()

import yaml
import time
import os
import codecs
import unittest
import pickle
import shutil
import base64
import tarfile
import io
import urlparse

class Blogger:
    def __init__(self, dumpFile):
        self.feed = feedparser.parse(dumpFile)
        self.entries = [Entry(entry) for entry in self.feed.entries if self.is_post(entry)]

    @staticmethod
    def is_post(entry): 
        # tag.term looks like 'http://schemas.google.com/blogger/2008/kind#post' 
        return any([tag for tag in entry.tags if 'kind#post' in tag.term])

    def write_posts(self, targetPath):
        for entry in self.entries:
            entry.write_post(targetPath)

class Entry:
    def __init__(self, feedEntry):
        self.feedEntry = feedEntry
        fileNameDate = self.blogofile_date('published').replace('/', '-')
        self.build_header()
        dateNameFile = fileNameDate + self.feedEntry.title.replace('/', '-') + '.html'
        if self.data['draft']:
            self.postFile = dateNameFile 
        else:
            permalink = self.data['permalink']
            bloggerSlug = os.path.basename(urlparse.urlsplit(permalink)[2])
            self.postFile = time.strftime("%Y-%m-%d", self.feedEntry.published_parsed) + '-' + bloggerSlug

    def build_header(self):
        allTags = self.feedEntry.tags
        tags = [tag.term for tag in allTags 
                        if not 'schemas.google.com' in tag.term]

        data = {'tags': tags,
                'date': self.blogofile_date('published'),
                'updated': self.blogofile_date('updated'),
                'title': self.feedEntry.title,
                'encoding': 'utf8',
                'draft': bool('app_draft' in self.feedEntry.keys() and 
                               self.feedEntry.app_draft == 'yes'),
                'author': self.feedEntry.author_detail.name}

        if 'link' in self.feedEntry.keys():
            data['permalink'] = urlparse.urlparse(self.feedEntry['link']).path

        self.data = data


    def write_post(self, targetPath):
        entryPath = os.path.join(targetPath, self.postFile)

        if os.path.isfile(entryPath):
            print >> sys.stderr, "Skipping.  Target file already exists: " + entryPath
        else:
            targetFile = open(entryPath, 'w')
            print >> targetFile, '---'
            print >> targetFile, self.blogofile_header()
            print >> targetFile, '---'
            targetFile.write(codecs.encode(self.feedEntry.content[0].value, 'utf8'))

    def blogofile_header(self):
        return yaml.safe_dump(self.data)

    def blogofile_date(self, dateType):
        dateStruct = {'published': self.feedEntry.published_parsed,
                      'updated': self.feedEntry.updated_parsed}[dateType]
        return time.strftime("%Y/%m/%d %H:%M:%S", dateStruct)

#base64 encoded test files gzipped tarballed as a python string
testData = (
"""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""")

testDataFile = io.BytesIO(base64.b64decode(testData))
testDataTar = tarfile.open("tar",  mode='r:gz', fileobj=testDataFile)
entryPickle = testDataTar.extractfile('feedparser-entry.pickle').read()
draftPickle = testDataTar.extractfile('feedparser-draft.pickle').read()

class MockBlogger(Blogger):
    def __init__(self):
        self.entries = [Entry(pickle.loads(entryPickle)),
                        Entry(pickle.loads(draftPickle))]

class TestBloggerfile(unittest.TestCase):
    def test_entry_header(self):
        entry = Entry(pickle.loads(entryPickle))
        header = yaml.load(entry.blogofile_header())
        assert 'barberry' in header['title'].lower()
        assert header['date'] == "2010/11/08 06:36:00"
        assert 'barberry' in header['permalink'].lower()
        assert 'food' in header['tags']
        assert header['updated'] == "2010/12/07 06:47:27" 
        assert header['author'] == "Seth de l'Isle"
        assert header['draft'] == False
        assert header['encoding'] == 'utf8'

    def test_draft_header(self):
        entry = Entry(pickle.loads(draftPickle))
        header = yaml.load(entry.blogofile_header())
        assert header['draft'] == True

    def test_write_posts(self):
        if os.path.isdir('test_data'):
            shutil.rmtree('test_data')

        os.mkdir('test_data')

        targetPath = os.path.join('test_data', '_posts')
        os.mkdir(targetPath)

        blogger = MockBlogger()
        blogger.write_posts(targetPath)
        assert os.path.isfile(os.path.join(targetPath, 
                                blogger.entries[0].postFile))
        assert os.path.isfile(os.path.join(targetPath,
                                blogger.entries[1].postFile))

        if os.path.isdir('test_data'):
            shutil.rmtree('test_data')

def display_error_and_usage(error):
    print >> sys.stderr, error
    print >> sys.stderr, "Usage: bloggerfile.py BloggerExportfile.xml"
    sys.exit()

if __name__ == '__main__':

        if '-t' in sys.argv:
            try:
                del sys.argv[sys.argv.index('-t')]
                unittest.main()
            except AttributeError:
                display_error_and_usage("Error: bad test option(s): " + " ".join(sys.argv[1:]))
        else:
            if len(sys.argv) > 2:
                display_error_and_usage("Error: extra options after Blogger export file: " + " ".join(sys.argv[2:]))
            try:
                dumpFile = sys.argv[1]
                if not os.path.isfile(dumpFile):
                    raise IOError
                blogger = Blogger(dumpFile)
                if not os.path.isdir('_posts'):
                    os.mkdir('_posts')
                blogger.write_posts('_posts')
            except IndexError:
                display_error_and_usage("Error: Please specify a Blogger export file.")
            except IOError:
                display_error_and_usage("Error: Couldn't read Blogger export file: " + sys.argv[1])
