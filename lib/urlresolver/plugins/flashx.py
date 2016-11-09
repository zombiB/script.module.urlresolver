"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi
    Updated by Gujal (c) 2016

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
from lib import jsunpack
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class FlashxResolver(UrlResolver):
    name = "flashx"
    domains = ["flashx.tv"]
    pattern = '(?://|\.)(flashx\.tv)/(?:embed-|dl\?|embed.php\?c=)?([0-9a-zA-Z/-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content

        cookie = response.get_headers(as_dict=True).get('Set-Cookie', {})
        cookie.update(self.__get_cookies(html))
        headers.update({'Cookie': cookie, 'Referer' : 'http://%s' % host})

        pattern = '[^"]+"\.\/(\w+\/\w+\.\w+).*?'  # api-js
        pattern += '"([^"]+%s[^"]+(?:\d+|)\.\w{1,3}\?\w+=[^"]+)".*?' % host  # cgi
        pattern += 'action=[\'"]([^\'"]+).*?'  # post-url
        pattern += '<input[^>]*name="imhuman"[^>]*value="(.*?)"[^>]*>.*?'  # imhuman
        pattern += '<span[^>]*id=["|\']\w+(?:\d+|)["|\'][^>]*>(\d+)<'  # countdown
        match = re.search(pattern, html, re.DOTALL | re.I)

        if not match:
            raise ResolverError('Site structure changed!')

        jscontent = self.net.http_GET('http://%s/%s' % (host, match.group(1)), headers=headers).content
        matchjs = re.search('\$\.adblock\s+!=\s+null.*?\$.get\(\'\.+\/(\w+\.\w+)\'[^{]+\{([^:]+).*?\'(.*?)\'', jscontent, re.DOTALL | re.I)

        if not matchjs:
            raise ResolverError('Site structure changed!')

        self.net.http_GET('http://www.%s/%s?%s=%s' % (host, matchjs.group(1), matchjs.group(2), matchjs.group(3)), headers=headers)

        self.net.http_GET(match.group(2).strip(), headers=headers)
        data = helpers.get_hidden(html)
        data[u'imhuman'] = match.group(4)
        common.kodi.sleep(int(match.group(5)) * 1000 + 500)
        html = self.net.http_POST(match.group(3), data, headers=headers).content

        sources = []
        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            packed_data = jsunpack.unpack(match.group(1))
            sources += self.__parse_sources_list(packed_data)
        return helpers.pick_source(sources)

    def __get_cookies(self, html):
        cookies = {}
        for match in re.finditer("\$\.cookie\(\s*'([^']+)'\s*,\s*'([^']+)", html):
            key, value = match.groups()
            cookies[key] = value
        return cookies

    def __parse_sources_list(self, html):
        sources = []
        match = re.search('sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
        if match:
            for match in re.finditer('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL):
                stream_url, label = match.groups()
                stream_url = stream_url.replace('\/', '/')
                sources.append((label, stream_url))
        return sources

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}')
