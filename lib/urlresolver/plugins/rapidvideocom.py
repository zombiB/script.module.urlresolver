# -*- coding: utf-8 -*-
"""
urlresolver XBMC Addon
Copyright (C) 2011 t0mm0

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
import random
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError


class RapidVideoResolver(UrlResolver):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        data = helpers.get_hidden(html)
        data['confirm.y'] = random.randint(0, 120)
        data['confirm.x'] = random.randint(0, 120)
        headers['Referer'] = web_url
        post_url = web_url + '#'
        html = self.net.http_POST(post_url, form_data=data, headers=headers).content.encode('utf-8')

        match = re.findall('''["']?sources['"]?\s*:\s*\[(.*?)\]''', html)
        if match:
            stream_urls = re.findall('''['"]?file['"]?\s*:\s*['"]?([^'"]+)['"]\s*,\s*['"]?label['"]?\s*:\s*['"]?([^'"p]+)''', match[0])
            if stream_urls:
                if len(stream_urls) == 1:
                    return stream_urls[0][0].replace('\/', '/') + helpers.append_headers(headers)
                elif len(stream_urls) > 1:
                    stream_urls = [(i[1], i[0]) for i in stream_urls]
                    stream_urls.sort(key=lambda i: int(i[0]), reverse=True)
                    stream_url = helpers.pick_source(stream_urls, self.get_setting('auto_pick') == 'true')
                    stream_url = stream_url.replace('\/', '/') + helpers.append_headers(headers)
                    return stream_url

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.rapidvideo.com/embed/{media_id}')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
