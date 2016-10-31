"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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
import random
import re
import urllib
from urlresolver import common
from lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError

class MovshareResolver(UrlResolver):
    name = "movshare"
    domains = ["movshare.net", 'wholecloud.net', 'vidgg.to']
    pattern = '(?://|\.)(movshare.net|wholecloud.net|vidgg.to)/(?:video/|embed(?:/|\.php)\?(?:v|id)=)([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        stream_url = ''
        match = re.search('<video.*?</video>', html, re.DOTALL)
        if match:
            links = re.findall('<source[^>]+src="([^"]+)', match.group(0), re.DOTALL)
            if links:
                stream_url = random.choice(links)

        if stream_url:
            return stream_url + helpers.append_headers({'Referer': web_url, 'User-Agent': common.FF_USER_AGENT})
        else:
            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        if 'vidgg' in host:
            template = 'http://{host}/embed/?id={media_id}'
        else:
            template = 'http://{host}/embed/?v={media_id}'
        return self._default_get_url(host, media_id, template)
