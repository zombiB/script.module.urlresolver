"""
    urlresolver XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

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

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import SiteAuth
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
from urlresolver.net import Net
import urlparse
import urllib
import json

class SimplyDebridResolver(Plugin, UrlResolver, SiteAuth, PluginSettings):
    implements = [UrlResolver, SiteAuth, PluginSettings]
    name = "Simply-Debrid"
    domains = ["*"]
    base_url = 'https://simply-debrid.com/kapi.php?'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.hosts = []
        self.patterns = []
        self.priority = int(p)
        self.net = Net()
        self.username = self.get_setting('username')
        self.password = self.get_setting('password')
        self.token = None

    def get_media_url(self, host, media_id):
        query = urllib.urlencode({'dl': media_id})
        url = self.base_url + query
        try:
            response = self.net.http_GET(url).content
            if response:
                common.log_utils.log_debug('Simply-Debrid: Resolved to %s' % (response))
                if response.startswith('http'):
                    return response
                else:
                    raise UrlResolver.ResolverError('Unusable Response from SD')
            else:
                raise UrlResolver.ResolverError('Null Response from SD')
        except Exception as e:
            raise UrlResolver.ResolverError('Link Not Found: Exception: %s' % (e))

    def login(self):
        try:
            query = urllib.urlencode({'action': 'login', 'u': self.username, 'p': self.password})
            url = self.base_url + query
            response = self.net.http_GET(url).content
            js_result = json.loads(response)
            if js_result['error']:
                msg = js_result.get('message', 'Unknown Error')
                raise UrlResolver.ResolverError('SD Login Failed: %s' % (msg))
            else:
                self.token = js_result['token']
        except Exception as e:
            raise UrlResolver.ResolverError('SD Login Exception: %s' % (e))
    
    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'simply-debrid.com', url

    def get_all_hosters(self):
        try:
            if not self.hosts:
                query = urllib.urlencode({'action': 'filehosting'})
                url = self.base_url + query
                response = self.net.http_GET(url).content
                self.hosts = [i['domain'] for i in json.loads(response)]
            common.log_utils.log_debug('SD Hosts: %s' % (self.hosts))
        except Exception as e:
            common.log_utils.log_error('Error getting Simply-Debrid hosts: %s' % (e))

    def valid_url(self, url, host):
        if self.get_setting('login') == 'false': return False
        self.get_all_hosters()
        if url:
            try: host = urlparse.urlparse(url).hostname
            except: host = 'unknown'
        if host.startswith('www.'): host = host.replace('www.', '')
        if any(host in item for item in self.hosts):
            return True

        return False

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_login" type="bool" label="login" default="false"/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_username" enable="eq(-1,true)" type="text" label="Username" default=""/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_password" enable="eq(-2,true)" type="text" label="Password" option="hidden" default=""/>\n' % (self.__class__.__name__)
        return xml

    def isUniversal(self):
        return True
