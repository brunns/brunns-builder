# encoding=utf-8
import email
import logging
from email.mime.text import MIMEText
from typing import NamedTuple, Optional

from more_itertools import nth

from brunns.builder import Builder, a_string, an_integer, method
from brunns.builder.internet import DomainBuilder

logger = logging.getLogger(__name__)


class EmailAddressBuilder(Builder):
    username = a_string
    domain = DomainBuilder

    def build(self):
        return "{0}@{1}".format(self.username, self.domain)


MimeEmailAddress = NamedTuple("MimeEmailAddress", [("address", str), ("name", Optional[str])])


class MimeEmailAddressBuilder(Builder):
    target = MimeEmailAddress

    address = EmailAddressBuilder
    name = lambda: " ".join(a_string() for _ in range(an_integer(1, 3)))


class EmailMessageBuilder(Builder):
    to_ = [MimeEmailAddressBuilder().build() for _ in range(an_integer(1, 3))]
    cc_ = [MimeEmailAddressBuilder().build() for _ in range(an_integer(1, 3))]
    bcc_ = [MimeEmailAddressBuilder().build() for _ in range(an_integer(1, 3))]
    from_ = MimeEmailAddressBuilder
    subject = a_string
    body_text = a_string

    @method
    def with_to(self, *args):
        if args and isinstance(args[0], str):
            return self.with_to_([MimeEmailAddress(args[0], nth(args, 1, None))])
        else:
            return self.with_to_([MimeEmailAddress(t[0], nth(t, 1, None)) for t in args])

    @method
    def and_to(self, *args):
        return self.with_to(*args)

    @method
    def plus_to(self, address: str, name: Optional[str] = None):
        self.to_ += [MimeEmailAddress(address, name)]
        return self

    @method
    def with_cc(self, *args):
        if args and isinstance(args[0], str):
            return self.with_cc_([MimeEmailAddress(args[0], nth(args, 1, None))])
        else:
            return self.with_cc_([MimeEmailAddress(t[0], nth(t, 1, None)) for t in args])

    @method
    def and_cc(self, *args):
        return self.with_cc(*args)

    @method
    def plus_cc(self, address: str, name: Optional[str] = None):
        self.cc_ += [MimeEmailAddress(address, name)]
        return self

    @method
    def with_bcc(self, *args):
        if args and isinstance(args[0], str):
            return self.with_bcc_([MimeEmailAddress(args[0], nth(args, 1, None))])
        else:
            return self.with_bcc_([MimeEmailAddress(t[0], nth(t, 1, None)) for t in args])

    @method
    def and_bcc(self, *args):
        return self.with_bcc(*args)

    @method
    def plus_bcc(self, address: str, name: Optional[str] = None):
        self.bcc_ += [MimeEmailAddress(address, name)]
        return self

    @method
    def with_from(self, address: str, name: Optional[str] = None):
        return self.with_from_(MimeEmailAddress(name, address))

    @method
    def and_from(self, address: str, name: Optional[str] = None):
        return self.with_from(name, address)

    def build(self):
        message = MIMEText(self.body_text)
        message["To"] = ", ".join(email.utils.formataddr((r.name, r.address)) for r in self.to_)
        message["CC"] = ", ".join(email.utils.formataddr((r.name, r.address)) for r in self.cc_)
        message["BCC"] = ", ".join(email.utils.formataddr((r.name, r.address)) for r in self.bcc_)
        message["From"] = email.utils.formataddr((self.from_.name, self.from_.address))
        message["Subject"] = self.subject
        return message
