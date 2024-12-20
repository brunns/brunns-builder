import logging
import string

from yarl import URL

from brunns.builder import Builder, a_string, an_integer, one_of

logger = logging.getLogger(__name__)


class DomainBuilder(Builder):
    subdomain = lambda: a_string(characters=string.ascii_lowercase)
    tld = lambda: one_of("com", "net", "dev", "co.uk", "gov.uk", "ng")

    def build(self):
        return f"{self.subdomain}.{self.tld}"


class UrlBuilder(Builder):
    target = URL

    scheme = lambda: one_of("http", "https", "tcp")
    user = a_string
    password = a_string
    host = DomainBuilder
    port = lambda: an_integer(1, 65535)
    path = lambda: [a_string(), a_string()]
    query = lambda: {a_string(): a_string(), a_string(): a_string()}
    fragment = a_string

    def build(self) -> URL:
        return URL.build(
            scheme=self.scheme,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=f"/{'/'.join(self.path)}",
            query=self.query,
            fragment=self.fragment,
        )
