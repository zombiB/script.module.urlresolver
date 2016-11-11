"""
flashx.tv urlresolver plugin
Copyright (C) 2015 tknorris

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import re
from lib import helpers
from urlresolver import common
from urlresolver.resolver import ResolverError

SORT_KEY = {'High': 3, 'Middle': 2, 'Low': 1}

def get_media_url(url):
    try:
        headers = {'User-Agent': common.FF_USER_AGENT}
        net = common.Net()
        html = net.http_GET(url, headers=headers).content
        match = re.search('''href=['"]([^'"]+)''', html)
        if match:
            html = net.http_GET(match.group(1), headers=headers).content
            headers.update({'Referer': url})
            html = helpers.add_packed_data(html)
        
        sources = helpers.parse_sources_list(html)
        try: sources.sort(key=lambda x: SORT_KEY.get(x[0], 0), reverse=True)
        except: pass
        source = helpers.pick_source(sources)
        return source + helpers.append_headers(headers)
        
    except Exception as e:
        common.log_utils.log_debug('Exception during flashx resolve parse: %s' % e)
        raise
    
    raise ResolverError('Unable to resolve flashx link. Filelink not found.')
