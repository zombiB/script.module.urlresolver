"""
    urlresolver XBMC Addon
    Copyright (C) 2016 Gujal

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

import re, xbmc
import urllib
from urlresolver import common
from lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError


class PlayHDResolver(UrlResolver):
    name = "playhd.video"
    domains = ["www.playhd.video", "www.playhd.fo"]
    pattern = '(?://|\.)(playhd\.(?:video|fo))/embed\.php?.*?vid=([0-9]+)[\?&]*'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        url = 'http://www.%s/'%host
        resp = self.net.http_GET(url)
        headers = dict(resp._response.info().items())
        xbmc.log(msg = 'headers : %s'%headers['set-cookie'], level = xbmc.LOGNOTICE)
        headers = {'Cookie': headers['set-cookie']}
        
        resp = self.net.http_GET(web_url, headers=headers)
        html = resp.content

        headers['User-Agent'] = common.FF_USER_AGENT
        headers['Referer'] = web_url

        r = re.findall('<source\s+src="(.*?)"', html)

        if r:
            stream_url = r[0] + helpers.append_headers(headers)
        else:
            raise ResolverError('no file located')

        return stream_url

    def get_url(self, host, media_id):
        return 'http://www.playhd.video/embed.php?vid=%s' % media_id
