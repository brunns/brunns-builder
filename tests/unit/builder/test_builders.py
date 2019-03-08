# encoding=utf-8
import email
import logging
import random
import string
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

import pendulum
import pytest
from brunns.matchers.object import has_identical_properties_to
from brunns.matchers.smtp import email_with
from furl import furl
from hamcrest import has_properties, assert_that, instance_of, not_

from brunns.builder import Builder, a_string, a_boolean, an_integer, one_of, method

logger = logging.getLogger(__name__)


def test_builder_using_only_defaults():
    # Given
    class SomeClass:
        def __init__(self, a, b=None, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_boolean

    builder = SomeClassBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=4))


def test_building_using_positional_args():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        args = [1, lambda: 2]
        c = "sausages"

    builder = SomeClassBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=1, b=2, c="sausages"))


def test_setting_values_by_with_method():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_string

    builder = SomeClassBuilder()

    # When
    actual = builder.with_a(99).build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=99))


def test_setting_values_by_kwargs():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_string

    # When
    actual = SomeClassBuilder(a=99).build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=99))


def test_values_and_factories():
    # Given
    class SomeClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = lambda: "sausages"

    builder = SomeClassBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=4, b="sausages"))


def test_multiple_builders_do_not_interfere():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = lambda: 4
        b = a_string

    builder1 = SomeClassBuilder()
    builder2 = SomeClassBuilder()

    # When
    actual1 = builder1.with_a(99).build()
    actual2 = builder2.build()

    # Then
    assert_that(actual1, not_(has_identical_properties_to(actual2)))


def test_furl_builder():
    # Given
    class DomainBuilder(Builder):
        subdomain = lambda: a_string(characters=string.ascii_lowercase)
        tld = lambda: one_of("com", "net", "dev", "co.uk", "gov.uk", "ng")

        def build(self):
            return "{0}.{1}".format(self.subdomain, self.tld)

    class FurlBuilder(Builder):
        target = furl

        scheme = lambda: one_of("http", "https", "tcp", None)
        username = a_string
        password = a_string
        host = DomainBuilder
        port = lambda: an_integer(1, 65535)
        path = lambda: [a_string(), a_string()]
        query = lambda: {a_string(): a_string(), a_string(): a_string()}
        fragment = a_string

    builder = FurlBuilder()

    # When
    url1 = builder.build()
    url2 = builder.build()
    url3 = builder.with_host("example.com").build()
    url4 = FurlBuilder().build()

    # Then
    assert_that(url1, instance_of(furl))
    assert_that(url1, has_identical_properties_to(url2))
    assert_that(url1, not_(has_identical_properties_to(url3)))
    assert_that(url1, not_(has_identical_properties_to(url4)))


def test_date_builder():
    # Given
    class DateBuilder(Builder):
        target = pendulum.date
        year = lambda: an_integer(1, 9999)
        month = lambda: an_integer(1, 12)
        day = lambda: an_integer(1, 28)

    # When
    actual = DateBuilder().build()

    # Then
    assert_that(actual, instance_of(date))


def test_path_builder_with_positional_args():
    # Given
    class PathBuilder(Builder):
        target = Path
        args = lambda: [a_string(), a_string()]

    # When
    actual = PathBuilder().build()

    # Then
    assert_that(actual, instance_of(Path))


def test_nested_builders():
    # Given
    class DomainBuilder(Builder):
        subdomain = lambda: a_string(characters=string.ascii_lowercase)
        tld = lambda: random.choice(["com", "net", "dev", "co.uk"])

        def build(self):
            return "{0}.{1}".format(self.subdomain, self.tld)

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

    builder = EmailMessageBuilder(subject="Chips are nice")

    # When
    actual = builder.with_to_name("simon").build()

    # Then
    assert_that(actual, instance_of(MIMEText))
    assert_that(actual.as_string(), email_with(to_name="simon", subject="Chips are nice"))


def test_additional_methods():
    # Given
    class MethodUsingBuilder(Builder):
        a = lambda: 4
        b = lambda: 7

        def build(self):
            return self.some_maths()

        @method
        def some_maths(self):
            return self.a + self.b

    # When
    actual = MethodUsingBuilder().build()

    # Then
    assert actual == 11


def test_neither_target_nor_build():
    # Given
    class BrokenBuilder(Builder):
        a = 4

    # When
    with pytest.raises(ValueError):
        BrokenBuilder().build()


def test_builder_as_object_proxy():
    # Given
    class SomeClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def mult(self):
            return self.a * self.b

        def __getitem__(self, item):
            return self.b

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = an_integer
        b = an_integer

    builder = SomeClassBuilder(a=2, b=3)

    # When

    # Then
    assert_that(builder, instance_of(SomeClassBuilder))
    assert builder.mult() == 6
    assert builder["whatever"] == 3
