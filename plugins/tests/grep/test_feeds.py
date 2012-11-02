'''
test_feeds.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import unittest

import core.data.kb.knowledgeBase as kb

from plugins.grep.feeds import feeds
from core.data.url.HTTPResponse import HTTPResponse
from core.data.request.fuzzable_request import FuzzableRequest
from core.data.parsers.url import URL
from core.data.dc.headers import Headers


class test_feeds(unittest.TestCase):
    
    def setUp(self):
        self.plugin = feeds()
        kb.kb.save('feeds', 'feeds', [])

    def tearDown(self):
        self.plugin.end()
        
    def test_rss(self):
        body = 'header <rss version="3"> footer'
        url = URL('http://www.w3af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body , headers, url, url)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)
        
        self.assertEquals( len(kb.kb.get('feeds', 'feeds')), 1 )
        i = kb.kb.get('feeds', 'feeds')[0]
        self.assertTrue( 'RSS' in i.get_desc() )
        self.assertTrue( '3' in i.get_desc() )
            
    def test_feed(self):
        body = 'header <feed foo="4" version="3"> footer'
        url = URL('http://www.w3af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body , headers, url, url)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)
        
        self.assertEquals( len(kb.kb.get('feeds', 'feeds')), 1 )
        i = kb.kb.get('feeds', 'feeds')[0]
        self.assertTrue( 'OPML' in i.get_desc() )
        self.assertTrue( '3' in i.get_desc() )

    def test_opml(self):
        body = 'header <opml version="3" foo="4"> footer'
        url = URL('http://www.w3af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body , headers, url, url)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)
        
        self.assertEquals( len(kb.kb.get('feeds', 'feeds')), 1 )
        i = kb.kb.get('feeds', 'feeds')[0]
        self.assertTrue( 'OPML' in i.get_desc() )
        self.assertTrue( '3' in i.get_desc() )
        
    def test_no_feeds(self):
        body = 'header <nofeed version="3" foo="4"> footer'
        url = URL('http://www.w3af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body , headers, url, url)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)
        
        self.assertEquals( len(kb.kb.get('feeds', 'feeds')), 0 )
    
    def test_no_version(self):
        body = 'header <rss foo="3"> footer'
        url = URL('http://www.w3af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body , headers, url, url)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)
        
        self.assertEquals( len(kb.kb.get('feeds', 'feeds')), 1 )
        i = kb.kb.get('feeds', 'feeds')[0]
        self.assertTrue( 'RSS' in i.get_desc() )
        self.assertTrue( 'unknown' in i.get_desc() )        
    
