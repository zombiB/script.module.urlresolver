"""
    Kodi urlresolver plugin
    Copyright (C) 2016  tknorris

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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError


class BlazefileResolver(UrlResolver):
    name = 'blazefile'
    domains = ['blazefile.co']
    pattern = '(?://|\.)(blazefile\.co)/(?:embed-)?([0-9a-zA-Z]+)'


    def __init__(self):
        self.net = common.Net()


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {'User-Agent': common.FF_USER_AGENT}

        html = self.net.http_GET(web_url, headers=headers).content

        if jsunpack.detect(html):
            html = jsunpack.unpack(html) + html

        url = re.findall('<param\s+name="src"\s*value="([^"]+)', html)
        url += re.findall('file\s*:\s*[\'|\"](.+?)[\'|\"]', html)
        url = [i for i in url if not i.endswith('.srt')]

        if url:
            return url[0] + '|%s' % urllib.urlencode(headers)

        raise ResolverError('Unable to locate link')


    def get_url(self, host, media_id):
        return 'http://www.blazefile.co/embed-%s.html' % media_id


