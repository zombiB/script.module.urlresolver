"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import urllib
from t0mm0.common.net import Net
from urlresolver import common
from urlresolver import HostedMediaFile
from urlresolver.plugnplay import Plugin
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings


class Video44Resolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "video44.net"
    domains = ["video44.net", "easyvideo.me"]
    pattern = 'http://((?:www.)?(?:video44.net|easyvideo.me))/gogo/.*?file=([%0-9a-zA-Z\-_\.]+).*?'
    
    def __init__(self):
        self.set_setting('enabled', 'true')
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_url(self, host, media_id):
        media_id = re.sub(r'%20', '_', media_id)
        return 'http://%s/gogo/?sv=1&file=%s' % (host, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r: return r.groups()
        else: return False

    def valid_url(self, url, host):
        return re.match(self.pattern, url) or self.name in host

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
                   'User-Agent': common.IE_USER_AGENT,
                   'Referer': web_url
                   }
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search('file\s*:\s*"(.+?)"', html)
        if not r:
            r = re.search('playlist:.+?url:\s*\'(.+?)\'', html, re.DOTALL)
        if r:
            if 'google' in r.group(1):
                return HostedMediaFile(url=r.group(1)).resolve()
            else:
                return r.group(1)
        else:
            raise UrlResolver.ResolverError('File not found')
