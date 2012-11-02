'''
wordpress_username_enumeration.py

Copyright 2011 Andres Riancho

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

import core.controllers.outputManager as om

# Import options
import re

from core.data.options.option_list import OptionList

from core.controllers.plugins.crawl_plugin import CrawlPlugin

import core.data.kb.knowledgeBase as kb
import core.data.kb.info as info

from core.controllers.w3afException import w3afRunOnce
from core.controllers.core_helpers.fingerprint_404 import is_404


# Main class
class wordpress_fullpathdisclosure(CrawlPlugin):
    '''
    Try to find the path where the WordPress is installed
    @author: Andres Tarantini ( atarantini@gmail.com )
    '''

    def __init__(self):
        CrawlPlugin.__init__(self)

        # Internal variables
        self._exec = True

    def crawl(self, fuzzable_request):
        '''
        @parameter fuzzable_request: A fuzzable_request instance that contains
        (among other things) the URL to test.
        '''
        possible_vulnerable_files = ['wp-content/plugins/akismet/akismet.php', 'wp-content/plugins/hello.php']

        # Search this theme path and add the themes header/footer to the possible vulnerable files
        domain_path = fuzzable_request.getURL().getDomainPath()
        response = self._uri_opener.GET( domain_path, cache=True )
        if not is_404( response ):
            response_body = response.getBody()
            theme_regexp = domain_path+'wp-content/themes/(.*)/style.css'
            theme = re.search(theme_regexp, response_body, re.IGNORECASE)
            if theme:
                theme_name = theme.group(1)
                possible_vulnerable_files.append(domain_path+'wp-content/themes/'+theme_name+'/header.php')
                possible_vulnerable_files.append(domain_path+'wp-content/themes/'+theme_name+'/footer.php')

        if not self._exec :
            # Remove the plugin from the crawl plugins to be run.
            raise w3afRunOnce()
        else:
            for vulnerable_file in possible_vulnerable_files:
                vulnerable_url = domain_path.urlJoin(vulnerable_file)
                response = self._uri_opener.GET( vulnerable_url, cache=True )

                if not is_404( response ):
                    response_body = response.getBody()
                    if 'Fatal error' in response_body:
                        if vulnerable_file in response_body:
                            # Unix-like
                            pass
                        elif vulnerable_file.replace('/', '\\') in response_body:
                            # Microsoft Windows (back slashes)
                            vulnerable_file = vulnerable_file.replace('/', '\\')
                        else:
                            vulnerrable_path = False

                        if vulnerable_file:
                            match = ' <b>(.*)'+vulnerable_file+'</b>'
                            path_disclosure = re.search(match, response_body, re.IGNORECASE)
                            if path_disclosure:
                                i = info.info()
                                i.setPluginName(self.get_name())
                                i.set_name('WordPress server path found')
                                i.setURL( vulnerable_url )
                                i.set_id( response.id )
                                desc = 'WordPress is installed on "%s"' % path_disclosure.group(1)
                                i.set_desc( desc )
                                kb.kb.append( self, 'info', i )
                                om.out.information( i.get_desc() )
                                break

        # Only run once
        self._exec = False

    def get_long_desc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin try to find the path in the server where WordPress is installed.

        The plugin will fail if WordPress is running on a Windows server due to paths manipulation (can be fixed, ToDo!).
        '''
