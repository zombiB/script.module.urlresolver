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
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class PutloadResolver(UrlResolver):
    name = "putload"
    domains = ["putload.tv"]
    pattern = '(?://|\.)(putload\.tv)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.FF_USER_AGENT}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url}
        headers.update(self.headers)
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.parse_sources_list(html)
        source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
        return source + helpers.append_headers(self.headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
