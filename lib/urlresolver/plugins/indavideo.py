# -*- coding: UTF-8 -*-
"""
    Kodi urlresolver plugin
    Copyright (C) 2016  alifrezser
    
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

import re, json
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class IndavideoResolver(UrlResolver):
    name = "indavideo"
    domains = ["indavideo.hu"]
    pattern = '(?://|\.)(indavideo\.hu)/(?:player/video/|video/)(.*)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content
        
        hash = re.search('emb_hash.+?value="(.+?)"', html)
        if not hash:
            raise ResolverError('File not found')
            
        url = 'http://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/' + hash.group(1)
            
        html = self.net.http_GET(url).content
        if '"success":"1"' in html:
            html = json.loads(html)['data']
            flv_files = html['flv_files']
            video_file = html['video_file']
            direct_url = video_file.rsplit('/', 1)[0] + '/' + flv_files[-1]
                
            return(direct_url)
        
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://indavideo.hu/video/%s' % (media_id)
