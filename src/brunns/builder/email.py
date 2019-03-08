# encoding=utf-8
import email
import logging
from email.mime.text import MIMEText

from brunns.builder import Builder, a_string
from brunns.builder.internet import DomainBuilder

logger = logging.getLogger(__name__)


class EmailBuilder(Builder):
    username = a_string
    domain = DomainBuilder

    def build(self):
        return "{0}@{1}".format(self.username, self.domain)


class EmailMessageBuilder(Builder):
    to_name = a_string
    to_email_address = EmailBuilder
    from_name = a_string
    from_email_address = EmailBuilder
    subject = a_string
    body_text = a_string

    def build(self):
        message = MIMEText(self.body_text)
        message["To"] = email.utils.formataddr((self.to_name, self.to_email_address))
        message["From"] = email.utils.formataddr((self.from_name, self.from_email_address))
        message["Subject"] = self.subject
        return message
