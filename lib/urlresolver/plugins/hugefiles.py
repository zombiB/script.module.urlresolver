'''
Hugefiles urlresolver plugin
Copyright (C) 2013 Vinnydude

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

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
import urllib, urllib2, re
from lib import captcha_lib

class HugefilesResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "hugefiles"
    domains = ["hugefiles.net"]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        common.addon.log_debug('HugeFiles: get_link: %s' % (web_url))
        html = self.net.http_GET(web_url).content

        r = re.findall('File Not Found', html)
        if r:
            raise UrlResolver.ResolverError('File Not Found or removed')

        # Grab data values
        data = {}
        r = re.findall(r'type="hidden"\s+name="(.+?)"\s+value="(.*?)"', html)
        
        if r:
            for name, value in r:
                data[name] = value
        else:
            raise UrlResolver.ResolverError('Unable to resolve link')

        data['method_free'] = 'Free Download'
        data.update(captcha_lib.do_captcha(html))

        common.addon.log_debug('HugeFiles - Requesting POST URL: %s with data: %s' % (web_url, data))
        html = self.net.http_POST(web_url, data).content

        # Re-grab data values
        data = {}
        r = re.findall(r'type="hidden"\s+name="(.+?)"\s+value="(.*?)"', html)
        
        if r:
            for name, value in r:
                data[name] = value
        else:
            raise UrlResolver.ResolverError('Unable to resolve link')

        data['referer'] = web_url

        headers = { 'User-Agent': common.IE_USER_AGENT }

        common.addon.log_debug('HugeFiles - Requesting POST URL: %s with data: %s' % (web_url, data))
        request = urllib2.Request(web_url, data=urllib.urlencode(data), headers=headers)

        try: stream_url = urllib2.urlopen(request).geturl()
        except: return

        common.addon.log_debug('Hugefiles stream Found: %s' % stream_url)
        return stream_url
 
    def get_url(self, host, media_id):
        return 'http://hugefiles.net/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)', url)
        if r:
            return r.groups()
        else:
            return False
        return('host', 'media_id')

    def valid_url(self, url, host):
        return (re.search('http://(www.)?hugefiles.net/' +
                         '[0-9A-Za-z]+', url) or
                         'hugefiles' in host)
