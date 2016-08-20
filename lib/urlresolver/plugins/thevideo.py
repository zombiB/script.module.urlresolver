'''
thevideo urlresolver plugin
Copyright (C) 2014 Eldorado

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
import os
import hashlib
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 3
PY_SOURCE = 'https://offshoregit.com/tvaresolvers/thevideo_gmu.py'
PY_PATH = os.path.join(common.plugins_path, 'thevideo_gmu.py')

class TheVideoResolver(UrlResolver):
    name = "thevideo"
    domains = ["thevideo.me"]
    pattern = '(?://|\.)(thevideo\.me)/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    @common.cache.cache_method(cache_limit=3)
    def get_gmu_code(self):
        try:
            new_py = self.net.http_GET(PY_SOURCE).content
            if new_py:
                with open(PY_PATH, 'w') as f:
                    f.write(new_py)
        except Exception as e:
            common.log_utils.log_warning('Exception during thevideo code retrieve: %s' % e)
            
    def get_media_url(self, host, media_id):
        try:
            if self.get_setting('auto_update') == 'true':
                self.get_gmu_code()
            with open(PY_PATH, 'r') as f:
                py_data = f.read()
            common.log_utils.log('thevideo_gmu hash: %s' % (hashlib.md5(py_data).hexdigest()))
            import thevideo_gmu
            web_url = self.get_url(host, media_id)
            return thevideo_gmu.get_media_url(web_url, host, self.get_setting('auto_pick') == 'true')
        except Exception as e:
            common.log_utils.log_debug('Exception during thevideo resolve parse: %s' % e)
            raise
            
    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        xml.append('<setting id="%s_auto_update" type="bool" label="Automatically update resolver" default="true"/>' % (cls.__name__))
        return xml
