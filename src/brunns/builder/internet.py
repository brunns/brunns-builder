# encoding=utf-8
import logging
import string

from furl import furl

from brunns.builder import Builder, a_string, an_integer, one_of

logger = logging.getLogger(__name__)


class DomainBuilder(Builder):
    subdomain = lambda: a_string(characters=string.ascii_lowercase)
    tld = lambda: one_of("com", "net", "dev", "co.uk", "gov.uk", "ng")

    def build(self):
        return "{0}.{1}".format(self.subdomain, self.tld)


class UrlBuilder(Builder):
    target = furl

    scheme = lambda: one_of("http", "https", "tcp", None)
    username = a_string
    password = a_string
    host = DomainBuilder
    port = lambda: an_integer(1, 65535)
    path = lambda: [a_string(), a_string()]
    query = lambda: {a_string(): a_string(), a_string(): a_string()}
    fragment = a_string
