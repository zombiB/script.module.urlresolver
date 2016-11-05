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

import re
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
        url = 'http://www.%s/' % (host)
        resp = self.net.http_GET(url)
        headers = resp.get_headers(as_dict=True)
        headers = {'Cookie': headers.get('set-cookie', ''), 'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.parse_html5_source_list(html)
        source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
        return source + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://www.playhd.video/embed.php?vid=%s' % (media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
