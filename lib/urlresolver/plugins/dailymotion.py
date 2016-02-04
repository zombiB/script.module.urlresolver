'''
dailymotion urlresolver plugin
Copyright (C) 2011 cyrus007

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
import xbmc
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re
import urllib2, urllib, json
from urlresolver import common

class DailymotionResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "dailymotion"
    domains = [ "dailymotion.com" ]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        html = re.search('({"context".+?)\);\n',html, re.DOTALL)
        if html:
            html = json.loads(html.group(1))
            if 'metadata' in html: html = html['metadata']
            else: return

        if 'error' in html:
            err_title = html['error']
            if 'title' in err_title:
                err_title = err_title['title']
            else:
                err_title = 'Content not available.'
            raise UrlResolver.ResolverError(err_title)

        if 'qualities' in html:
            html = html['qualities']

        videoUrl = []
        try: videoUrl.append(html['1080'][0]['url'])
        except: pass
        try: videoUrl.append(html['720'][0]['url'])
        except: pass
        try: videoUrl.append(html['480'][0]['url'])
        except: pass
        try: videoUrl.append(html['380'][0]['url'])
        except: pass
        try: videoUrl.append(html['240'][0]['url'])
        except: pass
        try: videoUrl.append(html['auto'][0]['url'])
        except: pass

        vUrl = ''
        vUrlsCount = len(videoUrl)
        if vUrlsCount > 0:
            q = self.get_setting('quality')
            if q == '0':
                # Highest Quality
                vUrl = videoUrl[0]
            elif q == '1':
                # Medium Quality
                vUrl = videoUrl[(int)(vUrlsCount / 2)]
            elif q == '2':
                # Lowest Quality
                vUrl = videoUrl[vUrlsCount - 1]

        return vUrl

    def get_url(self, host, media_id):
        return 'http://www.dailymotion.com/embed/video/%s' % media_id

    def get_host_and_id(self, url):
        match = re.search('//(.+?)/', url)
        if match:
            host = match.group(1)

        match = re.search('/swf/([\w]+)', url)
        if match:
            media_id = match.group(1)

        match = re.search('/sequence/([\w]+)', url)
        if match:
            media_id = match.group(1)

        match = re.search('/video/([\w]+)', url)
        if match:
            media_id = match.group(1)

        if host and media_id:
            return (host, media_id)
        else:
            return False


    def valid_url(self, url, host):
        return re.search('http://(www.)?dailymotion.com/sequence/[0-9A-Za-z]+', url) or \
                re.search('http://(www.)?dailymotion.com/video/[0-9A-Za-z]+', url) or \
                re.search('http://(www.)?dailymotion.com/swf/[0-9A-Za-z]+', url) or \
                re.search('http://(www.)?dailymotion.com/embed/[0-9A-Za-z]+', url) or \
                self.name in host

    #PluginSettings methods
    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting label="Video Quality" id="%s_quality" ' % self.__class__.__name__
        xml += 'type="enum" values="High|Medium|Low" default="0" />\n'
        return xml
