"""
openload.io urlresolver plugin
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
import urlparse
from urllib2 import HTTPError
from lib import helpers
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import ResolverError

net = common.Net()

def get_media_url(url, host, auto_pick=False):
    try:
        headers = {
            'User-Agent': common.IE_USER_AGENT,
            'Referer': url
        }
        html = net.http_GET(url, headers=headers).content
        html = re.sub("'\s*\+\s*'", '', html)
        sources = re.findall(r"'?label'?\s*:\s*'([^']+)p'\s*,\s*'?file'?\s*:\s*'([^']+)", html, re.I)
        if not sources:
            raise ResolverError('Unable to locate link')
        else:
            for match in re.finditer('"((?:https?://thevideo\.me)?/[^"]+)', html, re.I):
                js_url = match.group(1)
                if not js_url.lower().startswith('http'):
                    js_url = urlparse.urljoin('https://' + host, js_url)

                if host not in js_url.lower(): continue
                try:
                    js_data = net.http_GET(js_url, headers=headers).content
                except HTTPError:
                    js_data = ''
                
                match = re.search('(eval\(function.*?)(?:$|</script>)', js_data, re.DOTALL)
                if match:
                    js_data = jsunpack.unpack(match.group(1))
                
                r = re.search('vt\s*=\s*([^"]+)', js_data)
                if r:
                    source = helpers.pick_source(sources, auto_pick)
                    return '%s?direct=false&ua=1&vt=%s|User-Agent=%s' % (source, r.group(1), common.IE_USER_AGENT)

            else:
                raise ResolverError('Unable to locate js')
    except Exception as e:
        common.log_utils.log_debug('Exception during thevideo resolve: %s' % (e))
        raise
