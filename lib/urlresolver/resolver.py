#    urlresolver XBMC Addon
#    Copyright (C) 2011, 2016 t0mm0, tknorris
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
This module defines the interfaces that you can implement when writing
your URL resolving plugin.
'''
import abc
from urlresolver import common

abstractstaticmethod = abc.abstractmethod
class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class UrlResolver(object):
    __metaclass__ = abc.ABCMeta

    # TODO: Move this out of UrlResolver
    class ResolverError(Exception):
        pass
    
    class unresolvable():
        '''
        An object returned to indicate that the url could not be resolved
    
        This object always evaluates to False to maintain compatibility with
        legacy implementations.
    
        Args:
            code (int): Identifies the general reason a url could not be
            resolved from the following list:
                0: Unknown Error
                1: The url was resolved, but the file has been permanantly
                    removed
                2: The file is temporarily unavailable for example due to
                    planned site maintenance
                3. There was an error contacting the site for example a
                    connection attempt timed out
    
            msg (str): A string (likely shown to the user) with more
            detailed information about why the url could not be resolved
        '''
    
        def __init__(self, code=0, msg='Unknown Error'):
            self.code = code
            self.msg = msg
            self._labels = {}
    
            def __nonzero__(self):
                return 0

    '''
    Your plugin needs to implement the abstract methods in this interface if
    it wants to be able to resolve URLs (which is probably all plugins!)
    
    priority: (int) The order in which plugins will be tried. Lower numbers are tried first.
    domains: (array) List of domains handled by this plugin. (Use ["*"] for universal resolvers.)
    
    '''
    priority = 100
    domains = ['localdomain']
    
    @abc.abstractmethod
    def get_media_url(self, web_url):
        '''
        The part of your plugin that does the actual resolving. You must
        implement this method.

        Ths method will be passed the URL of a web page associated with a media
        file. It will only get called if your plugin's :meth:`valid_url` method
        has returned ``True`` so it will definitely be a URL for the file host
        (or hosts) your plugin is capable of resolving (assuming you implemented
        :meth:`valid_url` correctly!)

        The URL you return must be something that is playable by XBMC.

        If for any reason you cannot resolve the URL (eg. the file has been
        removed) then return ``False`` instead.

        Args:
            web_url (str): A URL to a web page associated with a piece of media
            content.

        Returns:
            If the ``web_url`` could be resolved, a string containing the direct
            URL to the media file, if not, returns ``False``.
        '''
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_url(self, host, media_id):
        raise NotImplementedError

    @abc.abstractmethod
    def get_host_and_id(self, url):
        raise NotImplementedError

    @abc.abstractmethod
    def valid_url(self, web_url, host):
        '''
        Determine whether this plugin is capable of resolving this URL. You must
        implement this method.

        The usual way of implementing this will be using a regular expression
        which returns ``True`` if the URL matches the pattern (or patterns)
        used by the file host your plugin can resolve URLs for.

        Args:
            web_url (str): A URL to a web page associated with a piece of media
            content.

        Returns:
            ``True`` if this plugin thinks it can resolve the ``web_url``,
            otherwise ``False``.
        '''
        raise NotImplementedError

    @classmethod
    def isUniversal(cls):
        '''
            You need to override this to return True, if you are implementing a univeral resolver
            like real-debrid etc., which handles multiple hosts
        '''
        return False

    def login(self):
        '''
        This method should perform the login to the file host site. This will
        normally involve posting credentials (stored in your plugin's settings)
        to a web page which will set cookies.
        '''
        return True

    @classmethod
    def get_settings_xml(cls):
        '''
        This method should return XML which describes the settings you would
        like for your plugin. You should make sure that the ``id`` starts
        with your plugins class name (which can be found using
        :attr:`self.__class__.__name__`) followed by an underscore.

        For example, the following is the code included in the default
        implementation and adds a priority setting::

            xml = '<setting id="%s_priority" ' % self.__class__.__name__
            xml += 'type="number" label="Priority" default="100"/>\\n'
            return xml

        Although of course you know the name of your plugin(!) so you can just
        write::

            xml = '<setting id="MyPlugin_priority" '
            xml += 'type="number" label="Priority" default="100"/>\\n'
            return xml

        The settings category will be your plugin's :attr:`UrlResolver.name`.

        I would link to some documentation of ``resources/settings.xml`` but
        I can't find any. Suggestions welcome!

        Override this method if you want your plugin to have more settings than
        just 'priority'. If you do and still want the priority setting you
        should include the priority code as above in your method.

        Returns:
            A string containing XML which would be valid in
            ``resources/settings.xml``
        '''
        xml = [
            '<setting id="%s_priority" type="number" label="Priority" default="100"/>' % (cls.__name__),
            '<setting id="%s_enabled" ''type="bool" label="Enabled" default="true"/>' % (cls.__name__)
        ]
        return xml

    @classmethod
    def set_setting(cls, key, value):
        common.set_setting('%s_%s' % (cls.__name__, key), str(value))

    @classmethod
    def get_setting(cls, key):
        '''
        .. warning::

            Do not override this method!

        Gets a setting that you have previously defined by overriding the
        :meth:`get_settings_xml` method.

        When requesting a setting using this method, you should not include
        the ``MyPlugin_`` prefix of the setting id you defined in
        :meth:`get_settings_xml`.

        For example, if you defined a setting with an id of
        ``MyPlugin_username``, you would get the setting from your plugin
        using::

            self.get_setting('username')

        Args:
            key (str): The name of the setting to retrieve (without the prefix).

        Returns:
            A string containing the value stored for the requested setting.
        '''
        return common.get_setting('%s_%s' % (cls.__name__, key))

    @classmethod
    def _get_priority(cls):
        try: return int(cls.get_setting('priority'))
        except: return 100
        