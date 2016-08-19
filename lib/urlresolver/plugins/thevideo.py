'''
thevideo urlresolver plugin
Copyright (C) 2014 Eldorado

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
'''
import re
import urlparse
from urllib2 import HTTPError
from lib import helpers
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 3

class TheVideoResolver(UrlResolver):
    name = "thevideo"
    domains = ["thevideo.me"]
    pattern = '(?://|\.)(thevideo\.me)/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.IE_USER_AGENT,
            'Referer': web_url
        }
        html = self.net.http_GET(web_url, headers=headers).content
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
                    js_data = self.net.http_GET(js_url, headers=headers).content
                except HTTPError:
                    js_data = ''
                
                match = re.search('(eval\(function.*?)(?:$|</script>)', js_data, re.DOTALL)
                if match:
                    js_data = jsunpack.unpack(match.group(1))
                
                r = re.search('vt\s*=\s*([^"]+)', js_data)
                if r:
                    source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
                    return '%s?direct=false&ua=1&vt=%s|User-Agent=%s' % (source, r.group(1), common.IE_USER_AGENT)

            else:
                raise ResolverError('Unable to locate js')
            
    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
