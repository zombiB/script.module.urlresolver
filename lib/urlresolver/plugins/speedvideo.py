'''
SpeedVideo.net urlresolver plugin
Copyright (C) 2014 TheHighway and tknorris

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
import base64
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class SpeedVideoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "speedvideo"
    domains = ["speedvideo.net"]
    domain = "speedvideo.net"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def valid_url(self, url, host):
        return re.match('http://(?:www.)?%s/(?:embed\-)?[0-9A-Za-z_]+(?:\-[0-9]+x[0-9]+.html)?' % self.domain, url) or 'speedvideo' in host

    def get_url(self, host, media_id):
        return 'http://speedvideo.net/embed-%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search('http://(?:www\.)?(%s)\.net/(?:embed-)?([0-9A-Za-z_]+)(?:-\d+x\d+.html)?' % self.name, url)
        if r:
            return r.groups()
        else:
            return False

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        a = re.compile('var\s+linkfile *= *"(.+?)"').findall(html)[0]
        b = re.compile('var\s+linkfile *= *base64_decode\(.+?\s+(.+?)\)').findall(html)[0]
        c = re.compile('var\s+%s *= *(\d*)' % b).findall(html)[0]

        stream_url = a[:int(c)] + a[(int(c) + 10):]
        stream_url = base64.b64decode(stream_url)

        return stream_url
